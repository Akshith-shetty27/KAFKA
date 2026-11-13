# KAFKA

AI-powered interview preparation for engineering students: coding patterns, aptitude,
core CS, and an AI mentor (ASK KAFKA).

**Stack:** Vue 3 · Vite · Tailwind CSS v4 · Vue Router · Pinia · Axios — Django · Django REST Framework ·
SimpleJWT — PostgreSQL 16.

Docs: [Architecture](docs/ARCHITECTURE.md) · [Design](docs/DESIGN.md) · [Progress](docs/PROGRESS.md)

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
- `LLM_PROVIDER=fake` runs ASK KAFKA offline; set `anthropic` + `ANTHROPIC_API_KEY` for real answers.
