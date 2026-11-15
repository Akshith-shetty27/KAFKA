# KAFKA — System Architecture

Status: **Proposed** — Phase 0 (architecture). No code has been written yet.

---

## 1. System overview

```
┌──────────────────────────────────────────────────────────────────────┐
│ Browser — Vue 3 SPA (Vite, Tailwind, Vue Router, Pinia, Axios)       │
│   views → stores (Pinia) → services/*.api.js → http.js (Axios)       │
│   access token: in memory (Pinia)   refresh token: httpOnly cookie   │
└───────────────┬──────────────────────────────────────────────────────┘
                │ HTTPS · JSON · /api/v1/*      (SSE for AI streaming)
                │ dev: Vite :5174 proxies /api → :8000 (same origin)
┌───────────────▼──────────────────────────────────────────────────────┐
│ Django 5 + Django REST Framework                                      │
│   urls → views (thin) → serializers (validation) → services (logic)   │
│   apps: core · accounts · catalog · progress · assistant              │
│   auth: SimpleJWT (rotating refresh + blacklist), DRF permissions     │
└───────┬───────────────────────────────────────────────┬──────────────┘
        │ Django ORM                                    │ provider adapter
┌───────▼─────────────┐                     ┌───────────▼──────────────┐
│ PostgreSQL 16       │                     │ LLM provider (external)   │
│ users, content,     │                     │ selected by env:          │
│ progress, activity, │                     │ LLM_PROVIDER / LLM_MODEL  │
│ conversations       │                     │ key lives only in backend │
└─────────────────────┘                     └──────────────────────────┘
```

**Layering rule (backend):** views never contain business logic. A view parses the request
with a serializer, calls a function in `services.py` (writes) or `selectors.py` (reads), and
returns a serializer of the result. This keeps logic testable without HTTP.

**Layering rule (frontend):** components never call Axios directly. Views use Pinia stores or
composables; stores call `services/*.api.js`; only `services/http.js` knows about Axios,
base URLs, tokens and refresh.

---

## 2. Backend apps

| App | Responsibility | Key modules |
|---|---|---|
| `core` | Shared plumbing: timestamp base model, pagination class, exception handler (uniform error JSON), common permissions | `models.py`, `pagination.py`, `exceptions.py`, `permissions.py` |
| `accounts` | Custom `User` (email login), `UserProfile`, register/login/refresh/logout/me, password change | `services.py`, `cookies.py` (refresh-cookie helpers) |
| `catalog` | Content: Category → Topic → Question, patterns, coding details, solutions, MCQ options; content seeding command | `selectors.py`, `management/commands/seed_content.py`, `content/*.py` |
| `progress` | Per-user question state, MCQ answering, activity log, dashboard/analytics/streak/recommendations | `services.py` (writes), `selectors.py` (aggregations) |
| `assistant` | ASK KAFKA: conversations, messages, context building, prompts, provider adapters, streaming | `llm/`, `context.py`, `prompts.py`, `services.py` |
| `prep` (v2) | Study plans: pasted job description → validated, JD-specific roadmap (phases → items linked to catalog topics/patterns), item progress | `services.py` (generation + validation), `schema.py` (JSON Schema for structured output), `prompts.py`, `selectors.py` |

Why `progress` owns analytics: every dashboard number is an aggregation over progress and
activity tables. A separate analytics app would only re-import those models (duplicate surface).

---

## 3. Data model

### 3.1 Entity–relationship diagram

```
User 1───1 UserProfile
 │
 ├──< QuestionProgress >──┐            (unique: user + question)
 ├──< ActivityEvent       │ (question nullable)
 └──< Conversation ──< Message
          │ (question nullable: the context the chat is about)
          ▼
Category 1──< Topic 1──< Question ──1 CodingDetail      (coding only)
                │           │  ├──< Solution             (per language; also SQL)
         TopicSection?      │  ├──< QuestionOption       (MCQ only)
       (optional grouping)  │  └──>< Pattern  (M2M)       (coding patterns)
                            │
                  QuestionProgress.selected_option → QuestionOption (nullable)
```

### 3.2 Tables

**accounts**

| Model | Fields | Constraints / indexes |
|---|---|---|
| `User` (AbstractUser) | email (login), first_name, last_name, password (PBKDF2 hash), is_active, date_joined | `email` unique; `USERNAME_FIELD = "email"` |
| `UserProfile` | user (1:1), college, graduation_year, target_role, preferred_language, daily_goal, timezone, theme (`ink`/`paper`), created_at, updated_at | created by a service on registration, in the same transaction |

> The custom user model must exist **before the first migration** — Django cannot switch to one later without pain. That is why it is in Phase 2 step 1.

**catalog**

| Model | Fields | Constraints / indexes |
|---|---|---|
| `Category` | slug, name, description, glyph, order | slug unique. Seeded: `coding`, `aptitude`, `core-cs` |
| `TopicSection` | category FK, name, order | groups aptitude topics into Quantitative / Logical / Verbal. Optional — a topic may have none |
| `Topic` | category FK, section FK (nullable), slug, name, description, order | unique (category, slug) |
| `Pattern` | slug, name | slug unique (Two Pointers, Sliding Window, …) |
| `Question` | topic FK, slug, title, question_type (`coding` / `mcq` / `concept`), difficulty (`easy`/`medium`/`hard`), statement (markdown), explanation (markdown), patterns M2M, order, is_published, timestamps | slug unique; index (topic, difficulty); index (question_type) |
| `CodingDetail` | question 1:1, constraints, examples (JSON list of `{input, output, explanation}`), approach, time_complexity, space_complexity | only for `coding` questions (validated in service + `clean()`) |
| `Solution` | question FK, language, code, notes | unique (question, language). Used by coding and SQL questions |
| `QuestionOption` | question FK, label (A–D), text, order, is_correct | unique (question, label); **partial unique index: at most one `is_correct=True` per question** |

Design notes:
- Content is authored as Python modules (`apps/catalog/content/*.py`) rather than JSON so code and Markdown
  can be written as readable multi-line strings. `seed_content` validates everything first, then upserts by
  slug (options by label) so re-seeding never breaks existing user progress.
- Category → Topic → Question is a strict FK chain; a question's category is derived via its topic (not stored twice).
- `CodingDetail` is split out so `Question` doesn't carry a dozen columns that are NULL for aptitude/core questions.
- `examples` is JSON because examples are an ordered list of value objects that are only ever read together with their question; they are never queried or joined.
- `Solution` is its own table so a question can later have Python + Java + C++ (and SQL) without schema changes.

**progress**

| Model | Fields | Constraints / indexes |
|---|---|---|
| `QuestionProgress` | user FK, question FK, status (`attempted`/`completed`), answer_count (MCQ submissions), is_correct (nullable; MCQ latest), first_attempt_correct (nullable; fixed by first submission), selected_option FK (nullable, SET_NULL), first_attempted_at, completed_at, updated_at | unique (user, question); check: status valid; check: completed ⇒ completed_at set; index (user, status); index (user, -updated_at) |
| `ActivityEvent` | user FK, question FK (nullable), event_type (`attempted`, `completed`, `answered`, `ai_message`), is_correct (nullable), created_at | index (user, created_at) |

- `QuestionProgress` = **current state** ("is this done?"). `ActivityEvent` = **append-only history** ("what happened when?").
  Daily activity, the weekly bar chart, streaks and accuracy-over-time are aggregations over `ActivityEvent`
  (`TruncDate(created_at, tzinfo=user_tz)`), so no daily counters are stored twice.
- Streak = number of consecutive local days ending today (or yesterday) with ≥1 event.
- **When things are recorded:** opening a question → `attempted` (event logged at most once per question per
  local day). MCQ → every submission logs `answered`; the first *correct* answer sets status `completed`.
  Coding/concept → the student marks it `completed` themselves. Resetting deletes the progress row but keeps events.

**assistant**

| Model | Fields | Constraints / indexes |
|---|---|---|
| `Conversation` | user FK, title, question FK (nullable), mode (`chat`/`hint`/`explain`/`review`), created_at, updated_at | index (user, updated_at) |
| `Message` | conversation FK, role (`user`/`assistant`), content, provider, model, input_tokens, output_tokens, metadata (JSON: hint level, etc.), created_at | index (conversation, created_at) |

### 3.3 Privacy enforcement
Every user-owned queryset is built as `Model.objects.filter(user=request.user)` inside selectors, and object
lookups use that filtered queryset, so another user's id returns **404**, not 403 (doesn't leak existence).
Tests will cover cross-user access for every user-owned endpoint.

---

## 4. REST API (v1)

All endpoints under `/api/v1/`. JSON. Errors use one shape: `{"error": {"code", "message", "fields"?}}`.
Lists are paginated: `{"count", "next", "previous", "results"}` (page size 20, max 100).

**Auth & profile** — `accounts`

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `auth/register/` | public | create user + profile; returns access + sets refresh cookie |
| POST | `auth/login/` | public | returns access + sets refresh cookie |
| POST | `auth/refresh/` | refresh cookie | rotates refresh, returns new access |
| POST | `auth/logout/` | refresh cookie | blacklists refresh, clears cookie |
| GET / PATCH | `auth/me/` | JWT | user + profile |
| POST | `auth/change-password/` | JWT | |

**Catalog** — read-only, requires JWT (progress fields are merged per user)

| Method | Path | Notes |
|---|---|---|
| GET | `categories/` | `question_count`, `attempted_count`, `completed_count` (mine) |
| GET | `topics/?category=` | each topic with its section and my counts; one call serves the analytics page too |
| GET | `questions/?category=&topic=&difficulty=&status=&pattern=&search=&page=&page_size=` | paginated summaries with my `status` (`null` = not started) |
| GET | `questions/{slug}/` | full detail + my progress + `navigation {previous, next}`. Solutions ordered by my preferred language. MCQ: **correct option + explanation are omitted until I have answered** |
| GET | `patterns/` | |

**Progress**

| Method | Path | Notes |
|---|---|---|
| POST | `questions/{slug}/attempt/` | I opened this question (idempotent) |
| POST | `questions/{slug}/answer/` | MCQ: `{option_id}` → `{is_correct, correct_option_id, explanation, progress}`; graded **server-side** |
| PUT / DELETE | `questions/{slug}/progress/` | PUT `{"status": "completed"}` (coding/concept only) / DELETE resets my progress |
| GET | `progress/summary/` | `totals`, `answers` (MCQ accuracy), `streak {current, longest, active_today}`, `categories[]` |
| GET | `progress/activity/?days=7\|14\|30\|90\|365` | zero-filled daily series in my timezone: questions, completed, answered, ai_messages |
| GET | `progress/recent/?limit=10` | questions I touched most recently |
| GET | `progress/insights/` | per-topic completion + first-try MCQ accuracy, completion by difficulty, up to 3 focus areas (`low_accuracy` / `unfinished`) |
| GET | `progress/plan/` | today's plan (`daily_goal` spread round-robin over categories; today's completions shown as done) + one recommended topic per category |

Throttles (`ScopedRateThrottle`): `auth` 20/min (login, register), `auth_refresh` 60/min, `assistant` 40/hour —
all env-configurable.

**Assistant**

| Method | Path | Notes |
|---|---|---|
| GET | `assistant/status/` | `{provider, model, offline}` — the UI flags offline demo mode |
| GET / POST | `assistant/conversations/?question=` | list mine (with last-message preview) / create with optional `{question_slug}` |
| GET / DELETE | `assistant/conversations/{id}/` | messages + `capabilities {hint, explain, review}` |
| GET / POST | `prep/plans/` | list my study plans (with progress) / generate one: `{role, job_description, company?, candidate_info?, days_available?, hours_per_day?}` → 201 plan · 400 field errors · 422 `plan_rejected` (not a JD / no evidenced requirements) · 503 `plan_generation_failed` (AI busy, retryable) · 502 (AI misconfigured). Throttle scope `prep_plan` |
| GET / DELETE | `prep/plans/{id}/` | plan with requirements (+ evidence quotes), phases, items, linked topics with my progress |
| PATCH | `prep/plans/{id}/items/{item_id}/` | `{completed}` — tick an item off / undo |
| POST | `assistant/conversations/{id}/messages/` | `{content, mode: chat\|hint\|explain\|review, hint_level?}` → validation errors as JSON 4xx; otherwise **Server-Sent Events**: `start` (user message + conversation title) → many `token` → `done` (saved reply) or `error` (safe message, `retryable`, partial reply if any) |

Rate limit: DRF `ScopedRateThrottle` on the messages endpoint (e.g. 40/hour/user, env-configurable).

---

## 5. Authentication flow

```
login ─▶ POST auth/login ─▶ 200 {access, user}  + Set-Cookie: kafka_refresh (httpOnly, SameSite=Lax, path=/api/v1/auth/)
app load ─▶ POST auth/refresh (cookie) ─▶ new access   (silent re-login after page reload)
API call ─▶ Authorization: Bearer <access>
   401 ─▶ Axios interceptor: one shared refresh request (single-flight) ─▶ retry original ─▶ fail ⇒ logout + /login
logout ─▶ POST auth/logout ─▶ refresh blacklisted, cookie cleared, store reset
```

- Access token lifetime 10 min, refresh 7 days, rotation + blacklist (`rest_framework_simplejwt.token_blacklist`).
- Why not localStorage for tokens: any XSS could read them. The access token in memory is short-lived;
  the long-lived refresh token is unreadable by JavaScript.
- Router guard: routes with `meta.requiresAuth` wait for the initial silent refresh before deciding.

---

## 6. ASK KAFKA — AI service design

```
assistant/
  llm/
    base.py               LLMProvider protocol: stream(system, messages, max_tokens) → TextDelta… then Finished(LLMResult)
                          LLMError(user_message, retryable) — the only error type the rest of the app sees
    groq_provider.py      Groq adapter (official `groq` SDK) — default: openai/gpt-oss-120b, free tier
    anthropic_provider.py Claude adapter (official SDK) — optional, paid
    fake_provider.py      deterministic offline provider (tests, and dev until a key is set)
    registry.py           get_provider() — chosen by LLM_PROVIDER; per-provider default model and reply cap
  context.py              question context from the DB + the reveal rules + capabilities
  prompts.py              mentor instructions, then question context, then per-mode instructions
  services.py             stream_turn(): validate → save user msg → stream → save reply (whatever happens)
  views.py                SSE endpoint (StreamingHttpResponse), conversations CRUD, status
```

**Anti-spoiler rule — enforced by what the model is given, not only by prompting**

| Request | Model receives the reference solution? |
|---|---|
| chat / hint on a question not yet completed | No — statement, examples, constraints only (patterns hidden too) |
| explain / review (deliberate requests) | Yes |
| question already completed by this student | Yes |

For MCQs, `explain`/`review` are allowed only after the student has answered (otherwise the assistant would bypass
server-side grading); `hint` only before. The UI mirrors these `capabilities`, the server re-checks them.

**Hints** come in three levels (nudge → key insight → step outline, never final code); the drawer offers the next
level automatically.

**Default provider: Groq, `openai/gpt-oss-120b` (free tier).** Request: system prompt as the first message, then
history; `max_completion_tokens` 3000 (provider default), `reasoning_effort` from `LLM_EFFORT` (`low`/`medium`/
`high`; `xhigh`/`max` map to `high`), `include_reasoning=False` so the model's private reasoning never reaches the
student, streaming. Prompt caching is automatic on Groq. `finish_reason` `length` → reply marked "cut short",
`content_filter` → "declined". The client is created lazily: no `GROQ_API_KEY` → a clear "not configured" message
(and `configured: false` from `/assistant/status/`), never a crash. Errors are mapped to student-safe messages
(429 → "busy, free-tier limit reached", retryable). Free-tier limits are account-wide (≈30 RPM, 1K RPD, 8K TPM,
200K TPD at the time of writing), which is why reply size and history are budgeted.

**Optional Claude adapter** (`LLM_PROVIDER=anthropic`): `claude-opus-5-5`, effort, 16k reply cap, prompt caching,
server-side refusal fallbacks — kept for anyone who wants a paid, stronger model; covered by the same tests.

**History**: last 10 messages and at most ~12,000 characters (≈3k tokens; `LLM_HISTORY_MESSAGES`, `LLM_HISTORY_CHARS`) —
the student's newest message is always included; failed/empty replies skipped; consecutive same-role messages
merged; always starting with the student. Full history stays in Postgres with token counts per reply.

**Streaming**: Django `StreamingHttpResponse` with SSE; `X-Accel-Buffering: no` for proxies. Validation runs
*before* the generator starts so errors are proper 4xx JSON. If the student presses Stop or closes the page the
generator receives `GeneratorExit` and the partial reply is saved as `incomplete`. The browser uses `fetch` +
`ReadableStream` (`services/sse.js`) with the same token refresh as Axios (shared single-flight refresh).

**Rate limit**: `ScopedRateThrottle` scope `assistant`, `ASSISTANT_RATE` (default 40/hour/user).

## 7. Folder structure

```
website]/                       ← repo root (see PROGRESS.md: folder name)
├── README.md                   setup + run instructions
├── docs/
│   ├── ARCHITECTURE.md         this file
│   ├── DESIGN.md               visual direction + tokens
│   ├── PROGRESS.md             phase tracker, decision log
│   └── DEPLOYMENT.md           production setup (nginx, Gunicorn, HTTPS, backups)
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── config/
│   │   ├── settings/  base.py · dev.py · prod.py · test.py
│   │   ├── urls.py             mounts /api/v1/ from each app
│   │   ├── wsgi.py · asgi.py
│   └── apps/
│       ├── core/        models.py · pagination.py · exceptions.py · views.py (health) · testing.py · tests/
│       ├── accounts/    models.py · signals.py · serializers.py · services.py · cookies.py · views.py · urls.py · admin.py · tests/
│       ├── catalog/     models.py · serializers.py · selectors.py · views.py · urls.py · admin.py
│       │                management/commands/seed_content.py · content/{coding,aptitude,core_cs}.py · tests/
│       ├── progress/    models.py · serializers.py · services.py · selectors.py · views.py · urls.py · tests/
│       └── assistant/   models.py · serializers.py · services.py · context.py · prompts.py · admin.py
│                        llm/{base,registry,anthropic_provider,fake_provider}.py · views.py · urls.py · tests/
└── frontend/
    ├── index.html · vite.config.js · package.json · .env.example
    └── src/
        ├── main.js · App.vue            App.vue = <RouterView/> inside a layout only
        ├── assets/styles/main.css        Tailwind v4 + @theme tokens (Paper/Ink)
        ├── router/        index.js (routes + guards) · navigation.js
        ├── stores/        auth.js · assistant.js
        ├── services/      http.js · sse.js · auth.api.js · catalog.api.js · progress.api.js · assistant.api.js · system.api.js
        ├── composables/   useAsync.js · useForm.js · useChat.js
        ├── utils/         format.js (dates, percent, greeting, safeRedirect) · markdown.js (markdown-it + DOMPurify + highlight.js)
        ├── components/
        │   ├── ui/        KIcon · KLogo · KEyebrow · KArrowLink · KButton · KInput · KSelect · KCodeWindow
        │   │              KChecklist · KBarChart · KStat · KStreakBadge · KProgressBar · KDifficulty
        │   │              KSkeleton · KEmptyState · KErrorState · KMarkdown · KCodeBlock · KPagination · KHeatmap
        │   ├── layout/    PublicLayout · PublicHeader · AuthLayout · AppLayout · AppHeader · MobileMenu · AppFooter
        │   ├── dashboard/ DashboardPanel · StatsRow · TodayPlan · WeeklyActivity · CategoryProgress
        │   │              RecommendedTopics · RecentQuestions
        │   ├── catalog/   QuestionTable
        │   ├── question/  ExampleList · RevealPanel · McqOptions · QuestionAside · QuestionMobileBar
        │   └── assistant/ ChatThread · ChatMessage · ChatComposer · QuickActions · AssistantDrawer · DemoModeNote
        └── views/
            LandingView · auth/LoginView · auth/RegisterView · DashboardView
            PrepareView · PracticeView (/practice/:category = coding · aptitude · core-cs)
            QuestionView (/questions/:slug — coding · mcq · concept layouts)
            ProgressView (/progress) · AskKafkaView (/ask, /ask/:id) · SettingsView (profile) · SystemStatusView · NotFoundView
```

---

## 8. Dependencies (and why each one exists)

**Backend** (`requirements.txt`)

| Package | Why |
|---|---|
| `Django` 5.x, `djangorestframework` | the agreed stack |
| `djangorestframework-simplejwt` | JWT access/refresh + blacklist — the standard DRF JWT library |
| `django-cors-headers` | CORS for production when frontend and API are on different origins |
| `psycopg[binary]` 3 | PostgreSQL driver |
| `django-environ` | reads `.env` into typed settings |
| `groq` | default LLM adapter — Groq, GPT-OSS 120B (only imported inside `groq_provider.py`) |
| `anthropic` | optional Claude adapter (only imported inside `anthropic_provider.py`) |

Not added: django-filter (filters are 4 query params — hand-written in selectors), Celery/Redis (not needed for v1), pytest (Django's test runner + DRF `APITestCase` are enough).

**Frontend** (`package.json`)

| Package | Why |
|---|---|
| `vue`, `vue-router`, `pinia`, `axios` | the agreed stack |
| `tailwindcss`, `@tailwindcss/vite` | the agreed stack (Tailwind v4) |
| `markdown-it` + `dompurify` | render problem statements / AI answers as markdown, **sanitized** (AI output is untrusted HTML) |
| `highlight.js` (core + a few languages) | syntax highlighting in solution and chat code blocks |

Not added: chart libraries (the reference charts are simple SVG/CSS), UI kits (would fight the design system), icon packs (glyphs are typographic).

---

## 9. Environment variables

`backend/.env`
```
DJANGO_SECRET_KEY=            DJANGO_DEBUG=true            DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://kafka_app:<password>@localhost:5432/kafka_app
CORS_ALLOWED_ORIGINS=http://localhost:5174
JWT_ACCESS_MINUTES=10         JWT_REFRESH_DAYS=7
LLM_PROVIDER=groq             GROQ_API_KEY=                LLM_MODEL=           LLM_EFFORT=medium
LLM_MAX_TOKENS=0              ANTHROPIC_API_KEY=           (empty/0 → provider defaults)
ASSISTANT_RATE=40/hour
PREP_PLAN_RATE=10/hour        PREP_LLM_EFFORT=low          PREP_PLAN_MAX_TOKENS=4500
PREP_JD_MIN_CHARS=200         PREP_JD_MAX_CHARS=15000      PREP_JD_PROMPT_CHARS=5000
```
`frontend/.env`
```
VITE_API_BASE_URL=/api/v1
VITE_DEV_API_TARGET=http://127.0.0.1:8000
```

---

## 10. Testing strategy

- **Backend:** `APITestCase` per app — auth flow (register/login/refresh rotation/logout blacklist), permission tests
  (anonymous → 401, other user's data → 404), MCQ grading, progress idempotency, streak edge cases (timezone,
  gaps), assistant with `fake_provider` (no network, no cost).
- **Frontend:** manual verification in the browser for each page (loading/empty/error states, mobile width).
  Production build (`vite build`) must pass with no warnings before a phase is marked done.
- A phase is only marked done in `PROGRESS.md` after its checks have actually been run.
