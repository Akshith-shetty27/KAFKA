# KAFKA — Development Progress

Read this first when resuming work. It records where we are, what was decided, and what is open.
Details live in [ARCHITECTURE.md](ARCHITECTURE.md) and [DESIGN.md](DESIGN.md); setup in [../README.md](../README.md).

## Current status

**v1 complete (2026-11-14). v2 in progress ([PLAN-V2.md](PLAN-V2.md)):** study plans from a pasted job description
are done (2026-11-15). Next: expand the question banks (≥ 50 per aptitude topic, ≥ 15 per coding pattern), then
plan-aware ASK KAFKA chat. Code execution (LeetCode-style workspace) is descoped.

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
| 2 | Models + migrations, auth (JWT/cookie), catalog/progress APIs, seed command, API tests | Done |
| 3 | Design system (tokens, ui components), layouts, routing + guards, landing, auth pages, dashboard | Done (+ settings page) |
| 4 | Prepare hub, practice lists, coding / aptitude / core question pages, completion + MCQ grading | Done (+ bank grown to 162) |
| 5 | ASK KAFKA: provider layer, context, hints, streaming, conversation history | Done (Groq live answers need a key) |
| 6 | Analytics page, recommendations/plan, responsiveness pass, error/empty states, integration testing | **Done** |
| v2·A | Study plans: paste JD + role → AI analysis → phased roadmap linked to topics, progress tracking | **Done** |
| v2·B | Question banks: aptitude 650 (13 topics × 20/20/10), coding 210 (14 topics × 15, incl. Hashing, Sorting, Recursion & Backtracking, Greedy) | **Done** (generators: `manage.py generate_aptitude`; bank in `content/bank/`; 153 tests) |
| v2·C | Plan-aware ASK KAFKA chat (teach, generate questions, adapt plan, mock interview) | Planned |
| UI | UI/UX transformation (motion system, dashboard, practice/questions, Ask KAFKA, landing 3D, progress/settings, QA) — docs/UI-PLAN.md | **Done** |

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

### v2·A Study plans — what exists

- **Backend `apps.prep`:** `PreparationPlan` (role, company, pasted JD, background, days × hours, summary,
  requirements JSON with evidence quotes, model + token usage) → `PlanPhase` → `PlanItem` (category, importance,
  reason, subtopics, activities, hours, M2M topics/patterns, `completed_at`). Migration `prep/0001`.
- **AI:** new `LLMProvider.complete_json()` (Groq strict JSON Schema; Claude `output_config.format`; offline fake
  builds a schema-shaped demo). Groq retries once on `json_validate_failed`; 413 "request too large" explained.
- **Validation (`services.validate_plan`):** requirements without a real JD quote are dropped (< 2 left → 422);
  non-JDs rejected with the model's reason; unknown topic/pattern slugs dropped; values normalised; sizes capped;
  hours scaled to the student's budget; phases forced into preparation order. JD is passed as tagged data
  (prompt-injection test: hidden "ignore previous instructions" in a recipe → rejected as not a JD).
- **Frontend:** `/ask/plans/new` (form; role pre-filled from profile) and `/ask/plans/:id` (requirements with
  quotes, phased roadmap, tick-off with optimistic save, links into Practice with live topic progress); Ask KAFKA
  sidebar lists plans; empty chat offers "Build my plan". `KTextarea` added to the design system.
- **Measured (Groq free tier, 8k TPM):** medium reasoning used ~7.8k tokens and couldn't fit prompt + reply limit;
  low reasoning: ~2.2k in / ~3k out, 7–10 s, 3/3 live runs succeeded, all five phase kinds present.
- **Tests:** +30 (validation, API incl. privacy/throttle/errors, Groq JSON request shape/retry). 144 total.

### Phase 6 — what exists

Progress analytics
- `GET /progress/insights/`: per-topic completion and first-try MCQ accuracy, completion by difficulty, and up to
  three focus areas (topics with < 70% first-try accuracy over ≥ 2 tries first, then topics started but < 50%
  done). `focus_areas()` is a pure, unit-tested function.
- `/progress` page (nav "Progress", the reference's INTERVIEW slot): headline stats, 12-month activity heatmap
  (`KHeatmap`, accessible summary, scrolls inside its box on phones), progress by track and by difficulty, focus
  area cards linking to the filtered practice list, and a per-topic table with track tabs.

Polish
- Sticky mobile action bar on question pages (status · Ask Kafka · Done); content padded so nothing hides behind it.
- Focus management: the ASK KAFKA drawer and the mobile menu return focus to the button that opened them.
- Error-state audit: every data request on every page has a loading, error (with Retry) and empty state; the one
  gap found (practice topic sidebar) is fixed.
- Stale-deploy recovery: if a page chunk from an old build fails to load, the router reloads once onto the target.

Production readiness
- `config/settings/prod.py`: refuses to start without `DJANGO_ALLOWED_HOSTS`; `CSRF_TRUSTED_ORIGINS` (for the
  admin behind HTTPS), referrer policy, quieter logging. `check --deploy` clean except opt-in HSTS preload (W021).
- `docs/DEPLOYMENT.md`: one-origin nginx + Gunicorn (gthread workers for SSE) setup, env table, nginx config with
  buffering off for ASK KAFKA, verify steps, update procedure, backups, security checklist.

Integration
- `apps/core/tests/test_end_to_end.py`: one student's full journey through the real API — register → cookie
  restore after "reload" → browse → server-graded wrong answer → complete a coding question → summary / plan /
  insights / recent agree → ASK KAFKA review stream (offline provider) → activity counts the AI message → logout →
  refresh rejected.
- Browser sweep at 375px over all 13 routes: no horizontal overflow, correct titles; Progress page checked with a
  year of sample data at desktop and phone widths; mobile bar complete flow; focus return; no console errors.
- 114 backend tests pass; `vite build` clean; no pending migrations. Test account deleted.

### Phase 5 — what exists

Backend (`apps/assistant`)
- Models: `Conversation` (user, optional question, title) and `Message` (role, content, mode, hint level, status
  complete/incomplete/error/refused, provider/model, token counts incl. cache reads). Admin with inline messages.
- Provider layer (`llm/`): protocol + `AnthropicProvider` (official SDK, `claude-opus-5-5`, effort `medium`,
  streaming, automatic prompt caching, server-side refusal fallbacks) + `FakeProvider` (offline, labelled demo) +
  registry. Errors become `LLMError` with student-safe text; provider details are logged, never shown.
- `context.py`: question context built from the DB; **solution withheld** for chat/hint until the question is
  completed; `explain`/`review` include it; MCQ explain/review only after answering, hint only before.
- `prompts.py`: mentor rules → question context → mode block (cache-friendly order); 3 hint levels.
- `services.stream_turn`: validates first (proper 4xx), then streams; saves the reply on success, provider error,
  max-tokens cut-off, refusal, or client disconnect (partial reply kept as `incomplete`); logs an `ai_message`
  activity event (counts towards streak/daily activity).
- API: status, conversations list/create/detail/delete, SSE messages endpoint; `assistant` throttle scope.

Frontend
- `services/sse.js` (fetch + ReadableStream SSE client sharing the single-flight token refresh with Axios),
  `services/assistant.api.js`, `stores/assistant.js` (status + conversation list), `composables/useChat.js`.
- Components: `ChatThread` (follows the stream unless you scroll up), `ChatMessage` (Markdown via sanitized
  `KMarkdown`, typing indicator, status notes), `ChatComposer` (Enter/Shift+Enter, Stop, 4000-char guard),
  `QuickActions` (Hint n of 3 → Review → Explain, per capabilities), `AssistantDrawer`, `DemoModeNote`.
- `/ask` and `/ask/:id`: conversation list (delete), suggestions, general chat; conversations started from a
  question keep their quick actions and link back. Nav gains "Ask Kafka".
- Question pages: "Ask Kafka" card in the side rail opens the drawer (latest conversation for that question, created
  lazily on first message); "Ask Kafka why →" after a wrong MCQ answer.

Verification
- Backend: 97 tests (32 new): reveal rules (solution never in hint context; other users' progress never used),
  capability matrix, prompt order, SSE event sequence, persistence, activity logging, validation, provider error
  mid-stream, max-tokens and refusal handling, client disconnect, history building, throttling, cross-user 404s,
  and the Claude adapter against a stub client (request shape incl. effort/caching/fallbacks; error mapping).
- Live: tokens stream through the Vite proxy (first token ≈0.06 s); browser checks at 1440px and 375px — hint
  streaming and escalation, Stop (partial saved as `incomplete` server-side), MCQ wrong → "Ask Kafka why" → review,
  unanswered MCQ offers hint only, general chat creates/titles a conversation and updates the URL, delete, drawer
  history reload, body scroll lock, no console errors. Test accounts deleted.
- **Provider switch (2026-11-14):** default is now Groq · `openai/gpt-oss-120b`. 108 backend tests pass (11 new:
  Groq request shape incl. `include_reasoning=False`, effort mapping, finish-reason mapping, error mapping, missing
  key, registry defaults/overrides, history character budget). Live server checked without a key: status reports
  `configured: false` and a message returns the "not configured" error cleanly.
- **Not yet verified:** real Groq responses — no `GROQ_API_KEY` is configured. Check one hint + one explanation once
  a key is added (README "Turning on ASK KAFKA").

### Phase 4 — what exists

Pages (all signed-in, linked from the header: Home · Prepare · Practice · Settings)
- `/prepare` — Preparation hub: the three tracks with live progress, then every topic (grouped by section for
  aptitude) linking into the practice library.
- `/practice/:category` — one view serves the Coding, Aptitude and Core CS practice pages. Topic sidebar
  (dropdown on mobile), search (debounced), difficulty, status and — for coding — pattern filters, paginated
  results. All filters live in the URL; clicked filters add history entries (Back undoes them), typing replaces.
- `/questions/:slug` — question page; opening it records an *attempt*.
  - Coding: statement, examples, constraints, **Approach** and **Solution** behind deliberate reveals,
    highlighted code with language tabs + copy, "why it works", complexity, patterns (link to filtered list).
  - MCQ: real radio inputs → "Check answer" → server grading → correct option teal / wrong pick red (with
    screen-reader text), verdict + explanation; state restored from the API on reload; "Reset & try again".
  - Concept: model answer behind a reveal, SQL solution when present, "Mark as understood".
  - Sticky side rail: my status, complete/reset, facts, previous/next within the topic.
- Dashboard plan items and recent questions now link to question pages; recommended topics link to the filtered
  practice list.

Frontend plumbing
- `services/catalog.api.js`; question write calls (`attempt`, `answer`, `complete`, `reset`) in `progress.api.js`.
- `utils/markdown.js`: markdown-it with `html: false` + DOMPurify (defence in depth for Phase 5 AI output),
  external links `noopener`; highlight.js core with Python/Java/C++/JavaScript/SQL only. The question page chunk
  is lazy-loaded (≈75 kB gzip including these libraries).
- New UI: `KMarkdown`, `KCodeBlock`, `KPagination`; `.k-prose` typography and highlight colours in `main.css`.
- Header highlighting uses path prefixes (`match` in `router/navigation.js`).

Question bank — **162 questions** (was 67)
- Coding 41 (10 topics, 2 hard), Aptitude 61 (13 topics in 3 sections; new: Averages, Ratio & Proportion,
  Simple & Compound Interest, Direction Sense), Core CS 60 (≈10 per subject; 37 concept / 23 MCQ).
- Verification: every coding solution executed against its stated examples (44 checks — this caught and fixed one
  wrong example); every numeric aptitude key re-derived in code (25 checks) and the reasoning/verbal keys checked
  by hand; each MCQ has exactly one correct option; correct letters spread A 20 · B 22 · C 24 · D 18.

Verification (browser, desktop + 375px, throwaway test account — deleted afterwards)
- Hub counts and topic grids; practice filters (topic, difficulty, search) with URL + Back behaviour; pagination
  (20/page); coding page reveals + highlighting + mark solved; MCQ wrong → explanation → reset → correct →
  persisted after reload; concept page table + SQL highlighting; dashboard links; unknown track / unknown question
  states; no horizontal overflow on phones; no console errors. Backend 65 tests pass; `vite build` clean.

### Phase 3 — what exists

Design system (`frontend/src/assets/styles/main.css`, `components/ui/`)
- Tailwind v4 tokens: raw palette + four type families, and **semantic** utilities (`bg-canvas`, `text-fg`,
  `text-muted`, `border-rule`, `bg-accent`, `text-accent-text`, …) that resolve per surface. Any element with
  `data-surface="ink|paper"` flips everything inside it. Type utilities: `k-display`, `k-serif` (keeps case),
  `k-eyebrow`, `k-label`; layout: `k-container`, `k-grid` texture, `k-rise` entrance animation.
- Contrast: teal is a fill on Paper; teal *text* on Paper uses `teal-700`. Muted text ≥ 5:1 on both surfaces.
- Components: KIcon, KLogo, KEyebrow, KArrowLink, KButton, KInput (password reveal, aria-invalid/describedby),
  KSelect, KCodeWindow, KChecklist, KBarChart (accessible summary), KStat, KStreakBadge, KProgressBar
  (role=progressbar), KDifficulty, KSkeleton, KEmptyState, KErrorState.

Auth on the frontend
- `stores/auth.js`: access token **in memory only**; `init()` restores the session once per page load via the
  refresh cookie. `services/http.js`: interceptors attach the token and, on 401, run **one shared refresh** then
  retry; if refresh fails → session cleared → `/login?redirect=…&expired=1`. Auth endpoints use `skipAuth`.
- Router guards (`requiresAuth`, `guestOnly`), `safeRedirect()` blocks open redirects. Route `meta.surface`
  picks Paper/Ink; inside the app it follows the profile theme.

Pages
- Landing (from the references: hero, method, three tracks, Ask KAFKA teaser, "Show up" section).
- Login / Register (split layout; server field errors shown inline; browser timezone sent on register).
- Dashboard — all numbers from `/progress/*`: greeting, stats, today's plan, 7-day chart, progress by track,
  recommended topics, recently attempted; per-section loading / error+retry / empty states.
- Settings — profile & preferences (PATCH /auth/me), Ink/Paper theme (saved to profile), password change.
- Nav lists only built pages (`router/navigation.js`); Prepare/Practice/Progress/Ask KAFKA are added as built.

Verification (browser, 1440px and 375px)
- Landing matches the references; no horizontal overflow at 375px; mobile menu (focus, Escape, scroll lock).
- Guard redirect → login; wrong password message; weak-password field error; register → dashboard.
- Dashboard empty states (new user) and populated states (seeded activity: streak 4, 75% accuracy, weekly bars).
- Settings: nested field error (`profile.daily_goal`), save persisted in DB, theme switch persisted across reload.
- Token expiry: corrupted access token → 4×401 → **1** refresh → 4 retries succeed. Revoked refresh token →
  redirect to login with "session expired"; sign-in returns to the original page. Logout survives full reload.
- `safeRedirect` unit-checked (7 cases); `vite build` clean; backend 65 tests still pass. Test user deleted.

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
| D21 | Semantic colour utilities over per-surface CSS variables | One markup works on Paper and Ink; sections can flip locally |
| D22 | Axios interceptors receive auth via `installAuth()` instead of importing the store | Avoids a store ↔ http circular import |
| D23 | Dashboard sections fetch independently (no dashboard store) | Page-specific data; one failure doesn't blank the page |
| D24 | Question rows on the dashboard aren't links yet | Question pages arrive in Phase 4; no links to unbuilt pages |
| D25 | Settings page built in Phase 3 | Theme toggle + profile need it; brief lists a profile page |
| D26 | One `PracticeView` parameterised by track (`/practice/coding|aptitude|core-cs`) | Three pages, one implementation — no duplicated filter logic |
| D27 | Filters in the URL; clicks push history, search typing replaces | Shareable/refreshable views without a Back-button trap |
| D28 | Approach and solution hidden behind explicit reveals | Encourages attempting first — the hint-before-answer philosophy ASK KAFKA will extend |
| D29 | markdown-it (`html: false`) + DOMPurify, highlight.js core with 5 languages | Safe rendering now and for AI output later; small bundle |
| D30 | Question bank verified by executing solutions / recomputing answers before seeding | Wrong answers in a prep tool do real harm |
| D31 | Anti-spoiler rule enforced by withholding the solution from the model's context | A prompt instruction can be talked around; absent data can't leak |
| D32 | MCQ explain/review only after answering | Otherwise ASK KAFKA bypasses server-side grading |
| D33 | Mode per message (chat/hint/explain/review), not per conversation | One conversation per question can mix hints and explanations |
| D34 | Conversations created lazily on the first message | Opening the drawer doesn't litter history with empty chats |
| D35 | Claude defaults: Opus 5.5, effort `medium`, 16k max tokens, prompt caching, server-side refusal fallbacks | Quality tutoring with bounded per-message cost; all tunable via env |
| D36 | Partial replies are always saved (error / stop / disconnect) | History never has silent gaps; the model sees what the student saw |
| D37 | **Default LLM: Groq, `openai/gpt-oss-120b`, free tier** (user's choice); Claude adapter kept as optional | No pay-as-you-go cost; provider layer still allows switching by env var |
| D38 | Groq defaults: 3,000-token replies, `include_reasoning=False`, history ≤10 msgs / ~12k chars | Free tier is ~8K tokens/min account-wide; students only see answers, not raw reasoning |
| D39 | Provider client created lazily; missing key → clear "not configured" message + `configured` flag | A missing secret must not crash the server or confuse students |
| D40 | Focus areas from first-try accuracy, not overall accuracy | Retrying until correct shouldn't hide a weak topic |
| D41 | Insights in one endpoint; topic rows reuse the catalog's per-user counts | No duplicate counting logic; one request for the Progress page |
| D42 | Production serves SPA and API from one origin behind nginx | No CORS; the path-scoped refresh cookie works unchanged |
| D43 | Gunicorn `gthread` workers in production | Each streaming ASK KAFKA reply holds a thread; sync workers would starve |

## Open items

- **Groq API key:** configured and verified live (chat and study plans).
- **Free-tier capacity:** limits are per Groq account and shared by all students (≈1K requests and 200K tokens per
  day). Fine for development/demos; a real launch needs Groq's paid Developer tier or another provider.

- **Content volume:** 162 questions — D12 target reached. More can be added with the same format + `seed_content`.
- **Mobile question page:** the status / "Mark as solved" rail sits below the article on phones. A sticky bottom
  action bar would be friendlier (Phase 6 polish).
- **Your account:** you registered your own account during Phase 3 testing; it's untouched. Testing in Phase 4
  used a throwaway account (deleted). You were signed out of the browser pane for that test — sign in again there.
- **Dev-server notes:**
  - Django's autoreloader can die if settings reference an app before its package exists; restart `runserver`
    if the API suddenly returns 502 through the proxy.
  - Tailwind (dev server only) doesn't pick up classes from **newly created** `.vue` files until Vite restarts;
    edits to existing files are fine and production builds always see everything. Likely related to the `]` in
    the folder name — renaming the folder (e.g. `~/Desktop/kafka`) is worth trying.

## Next step

v1 is complete. Suggested order from here:
1. **Turn on ASK KAFKA:** add `GROQ_API_KEY` to `backend/.env`, restart Django, try a hint and an explanation.
2. **Deploy** following `docs/DEPLOYMENT.md`.
3. Possible v2 work (not started): more questions (same content format + `seed_content`), AI mock interviews (the
   reference's INTERVIEW idea), frontend unit tests (e.g. Vitest) for composables, email verification and password
   reset (needs an email provider), and a paid LLM tier or provider if student numbers exceed Groq's free limits.
