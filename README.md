# KAFKA

AI-powered interview preparation for engineering students: coding patterns, aptitude,
core CS, and an AI mentor (ASK KAFKA).

**Stack:** Vue 3 · Vite · Tailwind CSS v4 · Vue Router · Pinia · Axios — Django · Django REST Framework ·
SimpleJWT — PostgreSQL 16.

Docs: [Architecture](docs/ARCHITECTURE.md) · [Design](docs/DESIGN.md) · [Progress](docs/PROGRESS.md) · [Deployment](docs/DEPLOYMENT.md)

```
backend/    Django project (config/ = settings & urls, apps/ = domain apps)
frontend/   Vue SPA (src/views, components, stores, services, router, composables)
docs/       architecture, design system, progress log
```

## Prerequisites

Python 3.12+, Node 20+, PostgreSQL 16 running locally.

## First-time setup

### 1. Database

```bash
psql -d postgres -c "CREATE ROLE kafka_app LOGIN CREATEDB PASSWORD 'choose-a-password';"
```

```bash
psql -d postgres -c "CREATE DATABASE kafka_app OWNER kafka_app;"
```

`CREATEDB` is needed so Django's test runner can create its throwaway test database.

### 2. Backend

```bash
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`: set `DJANGO_SECRET_KEY` (generate with
`backend/.venv/bin/python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`)
and the password in `DATABASE_URL`. Then:

```bash
cd backend && .venv/bin/python manage.py migrate
```

Load the question bank (safe to re-run after editing `apps/catalog/content/*.py`):

```bash
cd backend && .venv/bin/python manage.py seed_content
```

Optional — an admin account for http://localhost:8000/admin/ (manage questions, users, progress):

```bash
cd backend && .venv/bin/python manage.py createsuperuser
```

### 3. Frontend

```bash
cd frontend && npm install && cp .env.example .env
```

## Running

Two terminals:

```bash
cd backend && .venv/bin/python manage.py runserver 127.0.0.1:8000
```

```bash
cd frontend && npm run dev
```

Open http://localhost:5174 — the status page should show Frontend / API / Database all **OK**.
Vite proxies every `/api/*` request to Django, so the browser only ever talks to one origin.

> **After editing `backend/.env`, stop the Django server (Ctrl+C) and start it again.** Auto-reload only watches
> `.py` files, and a reloaded worker inherits the old environment — a key added to `.env` while the server is
> running (e.g. `GROQ_API_KEY`) won't be seen until a full restart. Also make sure only one server is running on
> port 8000: Vite always proxies there (`VITE_DEV_API_TARGET`), whatever other port you start Django on.

## Tests & checks

```bash
cd backend && .venv/bin/python manage.py test --settings=config.settings.test
```

```bash
cd frontend && npm run build
```

## Notes

- The project folder name ends in `]`, so quote paths in the shell: `cd ~/Desktop/"website]"`.
- Secrets live only in `backend/.env` (git-ignored). The frontend never holds API keys.
- `LLM_PROVIDER=fake` runs ASK KAFKA offline (clearly labelled demo replies).

## Turning on ASK KAFKA (Groq · GPT-OSS 120B · free tier)

ASK KAFKA uses [Groq](https://groq.com/) with the open-weight model **`openai/gpt-oss-120b`**. Groq's free tier
costs nothing; you only need an account and an API key (no card required to start, as far as Groq's billing docs
indicate).

1. Sign up at [console.groq.com](https://console.groq.com/) and create a key under **API Keys**.
2. Put it in `backend/.env` (never in the frontend, never in git):

   ```
   LLM_PROVIDER=groq
   GROQ_API_KEY=<your key>
   ```

3. Restart the Django server. Until a key is set, ASK KAFKA shows "isn't set up yet" instead of answering.

**Free-tier limits are per Groq account, shared by everyone using your KAFKA deployment.** At the time of writing
Groq lists roughly 30 requests/minute, 1,000 requests/day, 8,000 tokens/minute and 200,000 tokens/day for this
model — check the **Limits** page in the Groq console for the current numbers. That's plenty for development and
demos (very roughly 40–60 ASK KAFKA messages a day at typical sizes), not for thousands of students. When a limit is
hit, students see "ASK KAFKA is busy right now (free-tier limit reached). Try again in a minute."

To stay inside the limits, replies are capped at 3,000 tokens and only the last ~3,000 tokens of conversation
history are sent. Tunables in `backend/.env`: `LLM_EFFORT` (`low`/`medium`/`high` reasoning), `LLM_MAX_TOKENS`
(0 = provider default), `LLM_MODEL` (e.g. `openai/gpt-oss-20b` for a smaller, faster model), `LLM_HISTORY_CHARS`,
and `ASSISTANT_RATE` (per-student limit, default `40/hour`).

**Other providers.** The provider layer also includes a Claude adapter (`LLM_PROVIDER=anthropic` +
`ANTHROPIC_API_KEY`, paid per token) and the offline `fake` provider. Switching never requires code changes.
