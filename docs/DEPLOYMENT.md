# Deploying KAFKA

A single Linux server (Ubuntu 24.04 or similar) running PostgreSQL, Django behind Gunicorn, and nginx serving the
built Vue app. Everything is served from **one origin** (`https://kafka.example.com`):

```
browser ──HTTPS──▶ nginx ─┬─ /              → frontend/dist (static SPA, index.html fallback)
                          ├─ /static/       → backend/staticfiles (Django admin assets)
                          └─ /api/, /admin/ → Gunicorn (Django) on 127.0.0.1:8000 ──▶ PostgreSQL
                                                                   └──────────────▶ Groq API (ASK KAFKA)
```

One origin means no CORS configuration and the refresh cookie (`Path=/api/v1/auth/`, `Secure`, `SameSite=Lax`) just
works. If you host the frontend elsewhere, set `CORS_ALLOWED_ORIGINS` and `DJANGO_CSRF_TRUSTED_ORIGINS` and serve
both over HTTPS.

---

## 1. Prerequisites

- Python 3.12+, Node 20+ (build machine only), PostgreSQL 16, nginx, a domain pointing at the server.
- A Groq API key (free tier) for ASK KAFKA — see README "Turning on ASK KAFKA".

## 2. Database

```bash
sudo -u postgres psql -c "CREATE ROLE kafka_app LOGIN PASSWORD '<strong password>';"
```

```bash
sudo -u postgres psql -c "CREATE DATABASE kafka_app OWNER kafka_app;"
```

(Production doesn't need `CREATEDB` — that was only for the test runner.)

## 3. Environment (`backend/.env` on the server, readable only by the app user)

| Variable | Production value |
|---|---|
| `DJANGO_SECRET_KEY` | a new random value — never reuse the development key |
| `DJANGO_DEBUG` | `false` |
| `DJANGO_ALLOWED_HOSTS` | `kafka.example.com` (required — startup fails without it) |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | optional; defaults to `https://<each allowed host>` |
| `DATABASE_URL` | `postgres://kafka_app:<password>@localhost:5432/kafka_app` |
| `CORS_ALLOWED_ORIGINS` | empty when frontend and API share one origin |
| `LLM_PROVIDER` / `GROQ_API_KEY` | `groq` / your key |
| `ASSISTANT_RATE` | per-student ASK KAFKA limit, e.g. `40/hour` |
| `DJANGO_LOG_LEVEL` | `WARNING` (default) |

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

## 4. Backend

```bash
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt gunicorn
```

```bash
cd backend && export DJANGO_SETTINGS_MODULE=config.settings.prod && .venv/bin/python manage.py migrate && .venv/bin/python manage.py collectstatic --noinput && .venv/bin/python manage.py seed_content
```

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.prod .venv/bin/python manage.py createsuperuser
```

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.prod .venv/bin/python manage.py check --deploy
```

The only expected warning is `security.W021` (HSTS preload), which is opt-in.

### Gunicorn (systemd unit `/etc/systemd/system/kafka.service`)

ASK KAFKA streams replies over Server-Sent Events, and each open stream occupies a worker thread for its duration —
so use **threaded workers**, not plain sync workers:

```ini
[Unit]
Description=KAFKA (Django)
After=network.target postgresql.service

[Service]
User=kafka
WorkingDirectory=/srv/kafka/backend
Environment=DJANGO_SETTINGS_MODULE=config.settings.prod
ExecStart=/srv/kafka/backend/.venv/bin/gunicorn config.wsgi:application \
    --bind 127.0.0.1:8000 --workers 3 --worker-class gthread --threads 8 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

`--timeout 120` leaves room for a long streamed reply (the LLM client itself times out after `LLM_TIMEOUT`, 60 s).

## 5. Frontend

```bash
cd frontend && npm ci && npm run build
```

`VITE_API_BASE_URL` defaults to `/api/v1`, which is correct for the one-origin setup. Copy `frontend/dist` to the
server (e.g. `/srv/kafka/frontend/dist`).

## 6. nginx (`/etc/nginx/sites-available/kafka`)

```nginx
server {
    listen 443 ssl http2;
    server_name kafka.example.com;
    # ssl_certificate / ssl_certificate_key — e.g. from certbot

    root /srv/kafka/frontend/dist;

    # Hashed build assets can be cached for a long time.
    location /assets/ { expires 1y; add_header Cache-Control "public, immutable"; }

    location /static/ { alias /srv/kafka/backend/staticfiles/; }

    # ASK KAFKA streaming: never buffer, keep the connection open.
    location /api/v1/assistant/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 120s;
    }

    location ~ ^/(api|admin)/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # SPA: unknown paths serve index.html so Vue Router can handle them.
    location / {
        try_files $uri /index.html;
        add_header Cache-Control "no-cache";
    }
}

server { listen 80; server_name kafka.example.com; return 301 https://$host$request_uri; }
```

The backend also sends `X-Accel-Buffering: no` on streams, so buffering stays off even if the dedicated location
block is missing.

## 7. Verify

- `https://kafka.example.com/api/v1/health/` → `{"status": "ok", "database": "ok"}`
- Register, open a question, mark it complete, check the dashboard updates.
- Open ASK KAFKA on a question and ask for a hint — text should appear progressively, not all at once.
- `https://kafka.example.com/admin/` loads (static files served) and you can sign in.

## 8. Updating

```bash
cd /srv/kafka && git pull && cd backend && .venv/bin/pip install -r requirements.txt gunicorn && DJANGO_SETTINGS_MODULE=config.settings.prod .venv/bin/python manage.py migrate && DJANGO_SETTINGS_MODULE=config.settings.prod .venv/bin/python manage.py collectstatic --noinput && DJANGO_SETTINGS_MODULE=config.settings.prod .venv/bin/python manage.py seed_content
```

Then rebuild and copy `frontend/dist`, and `sudo systemctl restart kafka`. Tabs that were open during the update
reload themselves when they request a page chunk from the old build.

## 9. Backups

```bash
pg_dump --format=custom --file=kafka_$(date +%F).dump kafka_app
```

Run it daily (cron or a systemd timer) and copy the file off the server. Question content can always be restored
with `seed_content`; user accounts, progress and conversations only live in the database.

## 10. Security checklist

- [ ] `DJANGO_DEBUG=false`, new `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` set
- [ ] HTTPS with automatic renewal; HTTP redirects to HTTPS (HSTS is on, 30 days by default)
- [ ] `backend/.env` owned by the app user, mode `600`; no keys in git or in the frontend build
- [ ] PostgreSQL only listens on localhost; the DB user isn't a superuser
- [ ] Admin account uses a strong, unique password
- [ ] `manage.py check --deploy` clean (except W021)
- [ ] Backups running and a restore has been tested
- [ ] Groq usage watched in the Groq console — free-tier limits are shared by all students
