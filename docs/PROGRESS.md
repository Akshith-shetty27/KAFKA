# KAFKA — Development Progress

Read this first when resuming work. It records where we are, what was decided, and what is open.
Details live in [ARCHITECTURE.md](ARCHITECTURE.md) and [DESIGN.md](DESIGN.md); setup in [../README.md](../README.md).

## Current status

**Phase 1 — Project foundation: done (verified 2026-11-13).** Next: Phase 2.

## Environment (verified 2026-11-13)

| Tool | Version | Notes |
|---|---|---|
| Node / npm | 26.7.0 / 11.19.0 | |
| Python | 3.13.6 | venv at `backend/.venv` |
| PostgreSQL | 16.15 (Homebrew) | service `postgresql@16`; role + db **`kafka_app`** |
| Django / DRF / SimpleJWT | 6.1.3 / 3.18.3 / 5.5.1 | pinned in `backend/requirements.txt` |
| Vue / Router / Pinia / Axios | 3.5 / 5.5 / 4.1 / 1.21 | |
| Vite / Tailwind | 8.3 / 4.3 | Tailwind via `@tailwindcss/vite`, tokens in `src/assets/styles/main.css` |

Workspace notes:
- Project folder is `~/Desktop/website]` (trailing `]`); quote it in shells.
- The project has its own git repo (`git init` done). `~` is also a git repo — never `git add` from `~`.
- A pre-existing Postgres database named **`kafka`** (Alembic tables `users`, `daily_plans`, `plan_items`) belongs to
  another project and is deliberately **not** used or modified. KAFKA uses `kafka_app`.
- Port 5173 is used by another local project (`~/Desktop/kafka-frontend 2`), so KAFKA's Vite runs on **5174**.

## Phase tracker

| Phase | Scope | Status |
|---|---|---|
| 0 | Architecture, data model, API, folder structure, design direction | Done — approved |
| 1 | Scaffold Django + Vue, Tailwind, Postgres db/role, env files, verify both servers start | **Done** |
| 2 | Models + migrations, auth (JWT/cookie), catalog/progress APIs, seed command, API tests | Next |
| 3 | Design system (tokens, ui components), layouts, routing + guards, landing, auth pages, dashboard | Not started |
| 4 | Prepare hub, practice lists, coding / aptitude / core question pages, completion + MCQ grading | Not started |
| 5 | ASK KAFKA: provider layer, context, hints, streaming, conversation history | Not started |
| 6 | Analytics page, recommendations/plan, responsiveness pass, error/empty states, integration testing | Not started |

### Phase 1 — what exists

Backend (`backend/`)
- `config/settings/{base,dev,prod,test}.py` — env-driven via `django-environ`; `manage.py` → dev, `wsgi/asgi` → prod.
- DRF defaults: JWT auth, **IsAuthenticated by default**, pagination (`apps/core/pagination.py`),
  uniform error shape (`apps/core/exceptions.py`).
- `apps/core` — `TimeStampedModel`, `GET /api/v1/health/` (public; checks the DB).
- `apps/accounts` — custom `User` (email login, lower-cased, unique) created **before** the first migration;
  all Django migrations applied to `kafka_app`.
- 6 tests passing (`manage.py test --settings=config.settings.test`); `check --deploy` on prod settings clean
  except the opt-in HSTS-preload warning.

Frontend (`frontend/`)
- Vite with `@` alias and `/api` proxy → Django; Tailwind v4 with Paper/Ink tokens + Google Fonts
  (Inter Tight, Instrument Serif, DM Sans, JetBrains Mono).
- `services/http.js` — the single Axios instance + error normalisation; `composables/useAsync.js`.
- Router with lazy views: `/status` (live API/DB check; `/` redirects here until the landing page exists),
  404 page.
- Verified in the browser: status page shows all OK; with Django stopped it shows OFFLINE + "Could not reach the
  server"; `npm run build` passes.

## Decisions log

| # | Decision | Reason |
|---|---|---|
| D1 | Custom `User` model with email login, created before the first migration | Django can't switch user models cleanly later |
| D2 | Refresh token in httpOnly cookie, access token in memory | Tokens unreadable by XSS; silent refresh on reload |
| D3 | `QuestionProgress` (state) + `ActivityEvent` (history); stats are computed | No duplicated counters; streak/daily activity derived |
| D4 | MCQ answers graded server-side; correct option hidden until answered | Frontend can't be trusted; avoids answer leaking in network tab |
| D5 | LLM behind a provider interface + fake provider for tests | Swappable provider; tests cost nothing |
| D6 | SSE streaming via `fetch` for the one chat endpoint; Axios everywhere else | Axios (XHR) can't consume token streams cleanly |
| D7 | Question content is original, authored for KAFKA, loaded by an idempotent `seed_content` command | No copyrighted problem text; reproducible DB |
| D8 | No code execution in v1 (per brief) | |
| D9 | Visual direction "Paper & Ink": references define the language; app defaults to Ink, toggle to Paper | Resolves brief (dark) vs references (light editorial) |
| D10 | INTERVIEW nav → PROGRESS (analytics) in v1; AI mock interviews deferred | Not in the brief's scope |
| D11 | Anthropic adapter first, `claude-opus-5-5` default, `LLM_PROVIDER=fake` until a key is added | Works offline; model changeable via env |
| D12 | Seed volume v1: ~40 coding, ~60 aptitude, ~60 core CS questions | Enough to make every page real |
| D13 | DB `kafka_app` (not `kafka`), Vite port 5174 | Avoid colliding with the user's other local projects |
| D14 | Health endpoint is public and returns only status flags | Needed by the status page; leaks nothing |

## Open items

- **LLM API key:** not configured yet. Add `ANTHROPIC_API_KEY` to `backend/.env` and set `LLM_PROVIDER=anthropic` before Phase 5 testing.

## Next step

Phase 2 — `UserProfile`, auth endpoints (register/login/refresh cookie/logout/me), catalog models
(Category → Topic → Question + details/solutions/options/patterns), progress models, serializers/selectors/services,
`seed_content` command, admin registration, and API tests (including cross-user access checks).
