# KAFKA — Development Progress

Read this first when resuming work. It records where we are, what was decided, and what is open.
Details live in [ARCHITECTURE.md](ARCHITECTURE.md) and [DESIGN.md](DESIGN.md); setup in [../README.md](../README.md).

## Current status

**Phase 2 — Database & backend APIs: done (verified 2026-11-13).** Next: Phase 3 (design system + auth pages + dashboard).

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
| 1 | Scaffold Django + Vue, Tailwind, Postgres db/role, env files, verify both servers start | Done |
| 2 | Models + migrations, auth (JWT/cookie), catalog/progress APIs, seed command, API tests | **Done** |
| 3 | Design system (tokens, ui components), layouts, routing + guards, landing, auth pages, dashboard | Next |
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

### Phase 2 — what exists

Backend apps
- `accounts` — `UserProfile` (college, graduation year, target role, preferred language, daily goal, IANA
  timezone, theme) auto-created by a `post_save` signal for every user (API, admin, createsuperuser).
  Endpoints: register, login, refresh (rotating, blacklisted), logout, me (GET/PATCH), change-password
  (signs out other sessions). Refresh token only ever in the httpOnly cookie (`Path=/api/v1/auth/`, `SameSite=Lax`).
  Login errors are identical for unknown email / wrong password. Login/register throttled.
- `catalog` — Category, TopicSection, Topic, Pattern, Question, CodingDetail, Solution, QuestionOption with
  DB constraints (valid enums, unique slugs, one solution per language, **at most one correct option** via a
  partial unique index). Read APIs with per-user progress; MCQ answers withheld until answered. Admin with inlines.
- `progress` — QuestionProgress (state) + ActivityEvent (history). Services: record_attempt, submit_answer
  (row-locked), mark_completed, reset_progress, log_event. Selectors: summary, streaks (pure function, timezone
  aware), daily activity (zero-filled), recent, today's plan + recommended topics.

Content (`manage.py seed_content`, idempotent)
- 67 original questions: Coding 21 (10 topics, 13 patterns, Python solutions), Aptitude 27 MCQs (3 sections,
  9 topics), Core CS 19 (6 subjects; concept answers, MCQs, SQL solutions).
- Every coding solution executed against its examples (24 checks); every aptitude answer key re-derived
  arithmetically; correct-answer letters spread across A–D.

Verification
- 65 backend tests passing (`manage.py test --settings=config.settings.test`): auth flow incl. rotation/replay,
  logout blacklist, password-change session revocation, throttling; catalog filters/pagination/answer hiding;
  progress writes; stats; streak + timezone edge cases; seed idempotency; **cross-user isolation** on every
  user-owned read and write.
- Live smoke test through the Vite proxy against Postgres: login → cookie refresh → catalog → answer MCQ →
  complete coding question → summary/plan/activity/recent → logout → refresh rejected.
- Query counts flat (question list of 50 = 4 queries; plan = 20, bounded by category count).

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
| D15 | Profile created by `post_save` signal | The only hook that sees every user-creation path |
| D16 | Opening a question = "attempted"; MCQ "completed" = first correct answer; coding/concept completed manually | Makes "attempted" vs "completed" meaningful per question type |
| D17 | Single `GET /questions/` with filters (and `GET /topics/?category=`) instead of nested routes | One endpoint per resource; no duplicate list logic |
| D18 | Progress counts merged from the user's own rows instead of a join over all users | Stays fast as the user base grows |
| D19 | Content as Python modules + validating, idempotent `seed_content` | Readable multi-line code/Markdown; re-seeding keeps option ids so progress survives |
| D20 | Bookmarks dropped from v1 | Not in the brief; would need a separate table to avoid fake "attempted" rows |

## Open items

- **LLM API key:** not configured yet. Add `ANTHROPIC_API_KEY` to `backend/.env` and set `LLM_PROVIDER=anthropic` before Phase 5 testing.

- **Content volume:** 67 of the ~160 planned questions (D12). The rest is added in Phase 4 using the same format.
- **Dev-server note:** Django's autoreloader can die if settings reference an app before its package exists;
  restart `runserver` if the API suddenly returns 502 through the proxy.

## Next step

Phase 3 — design system in Vue (tokens, `components/ui/*`), Public/App layouts, auth store with in-memory access
token + silent refresh + 401 interceptor, route guards, landing page, login/register pages, and the dashboard
wired to `progress/summary`, `progress/activity`, `progress/plan`, `progress/recent`.
