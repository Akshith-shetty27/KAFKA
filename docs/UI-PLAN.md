# KAFKA — UI/UX & Interaction Transformation Plan

Status: **Stages 1–5 done** — see §7. GSAP and Three.js approved; Three.js is added in Stage 6.
Scope: frontend only. No backend, model, API-contract or environment changes are needed for anything below.

---

## 1. Existing frontend assessment

Audited: `package.json`, router, stores, services, `main.css` tokens, all 40+ components/views, `docs/DESIGN.md`,
and the running app (landing, login, dashboard, practice, aptitude question, Ask KAFKA) at 1024 px.

### Strengths to keep

| Area | What exists |
|---|---|
| Design system | "Paper & Ink": semantic tokens (`bg-canvas`, `text-fg`, `border-rule`, `accent`…) that flip per surface; four type families (Inter Tight display, Instrument Serif italic, DM Sans, JetBrains Mono); `k-eyebrow / k-display / k-serif / k-label` utilities; grid texture; ~22 `components/ui/*` primitives. Distinctive editorial language — not a generic dashboard. |
| Architecture | Route-level code splitting, one Axios instance with single-flight refresh, Pinia stores, `useAsync` / `useForm` / `useChat` composables, SSE streaming. |
| Data honesty | Every dashboard number comes from `/progress/*`; no fake stats anywhere. |
| Accessibility basics | Labelled inputs, `:focus-visible` ring, `aria-*` on toggles and progress bars, a global `prefers-reduced-motion` rule, focus return in the assistant drawer. |
| Dependencies | Minimal: vue, router, pinia, axios, markdown-it, dompurify, highlight.js. No animation library yet (motion = one CSS `k-rise` keyframe). |

### Problems found (verified in the browser)

1. **Theme flash on every full page load.** The app renders on Paper, then switches to Ink once `/auth/me` returns;
   `body` fades its background over 250 ms while text colour flips instantly, so headings are briefly invisible
   (seen on dashboard, practice, question and Ask KAFKA loads). Fix: remember the last surface and set
   `data-surface` from an inline script in `index.html` before Vue mounts.
2. **Motion is flat.** Pages appear all at once; no route transitions, no feedback when progress changes
   (stats, bars and the streak just re-render), no scroll storytelling on the landing page.
3. **Dashboard hierarchy.** A large greeting with empty space, four plain number cells, a 7-day bar chart (the 1-year
   `KHeatmap` only lives on the Progress page), one combined "Aptitude" track (the brief wants Quantitative and
   Logical separately — the topic API already returns sections, so no backend change is needed).
4. **Question pages.** Correct/incorrect states are clear but static; explanations appear without transition; no
   per-topic position indicator ("question 7 of 50").
5. **Ask KAFKA.** Functional streaming chat with a basic "thinking" dots state and a streaming caret, but no message
   entrance, no assistant identity mark, and code inside chat answers has no copy button (solution code blocks
   already do, via `KCodeBlock`).
6. **No notification system.** Successes/errors render inline only; there is no shared toast for actions like
   "Plan saved" or "Couldn't save — retry".

(To check during the stages: tablet breakpoints of the practice sidebar, keyboard order in the question aside.)

---

## 2. Proposed visual direction — "Ink & Signal"

Evolve Paper & Ink rather than replace it. The authenticated app is already Ink by default (user can switch to
Paper in Settings), which matches the brief's "deep dark backgrounds".

- **Surfaces:** keep ink-950 canvas / ink-900 panels / ink-850 raised. Add one **elevation token** (a 1 px inner top
  highlight + soft shadow) for interactive cards instead of glows or glass.
- **Accent:** teal `#22dcc8` stays the single action colour. Add **one cool secondary** (a desaturated cyan, for data
  series only) so charts can show two series without introducing a second "brand" colour.
- **Light, not neon:** the only gradients are low-opacity *light pools* (radial, ≤ 8 % alpha) behind the landing hero
  and the assistant's identity mark. No glowing borders, no glassmorphism.
- **Type:** unchanged families. Display stays for page openers only; data UI uses mono numerals with tabular figures.
- **Motion language — precise, mechanical, editorial:** rules draw left → right, mono counters tick up, items rise in
  short staggers (≤ 60 ms apart, ≤ 500 ms total), progress rings sweep. Everything uses transform/opacity, eases out,
  and is skipped entirely under `prefers-reduced-motion`.
- **3D, once:** a single lazy-loaded Three.js scene on the landing hero — a slowly rotating lattice of points
  (one point per question in the bank, 920 today, coloured by track) that leans toward the cursor. Static SVG fallback
  for no-WebGL, low-power or reduced-motion. No 3D inside the app.

## 3. Component transformation plan

**Motion architecture (`src/motion/`)** — one place for GSAP:
- `gsap.js` registers plugins once (ScrollTrigger) and exposes `prefersReducedMotion()`.
- `useMotion(rootRef, setup)` — runs `setup` inside `gsap.context()` after mount, reverts it on unmount
  (kills tweens and ScrollTriggers), wraps everything in `gsap.matchMedia()` with a reduced-motion branch.
- `v-reveal` directive — ScrollTrigger batch reveals with cleanup in `unmounted`.
- `useCountUp(valueRef)` — animates numbers when real data arrives or changes.

**New / upgraded components**

| Component | Purpose |
|---|---|
| `KCountUp` | Animated numbers for stats (respects reduced motion; final value always in the DOM for screen readers). |
| `KProgressRing` | SVG ring that sweeps to its value; used for overall and per-track progress. |
| `KStatCard` | Stat cell with label, count-up, optional delta and ring. |
| `KTrackCard` | Interactive track card (Coding / Quantitative / Logical / Core CS) with ring, hover depth, keyboard focus. |
| `KToast` + `useToast` | Polished success/error notifications, `aria-live`, auto-dismiss, keyboard-closable. |
| `KAssistantMark` | Small SVG identity mark for KAFKA that animates only while a reply streams (replaces the plain dots). |
| `KCopyButton` | Copy-to-clipboard for code inside chat answers (shared with `KCodeBlock`), with confirmation state. |
| `KTransition` presets | Route transition (fade + 8 px rise) and panel/modal transitions, CSS-based. |
| `HeroScene` (lazy) | The landing Three.js lattice; separate chunk; paused off-screen / tab hidden. |

**Pages (in order):** Dashboard → Prepare/Practice → Coding question → Aptitude question → Core CS reading →
Ask KAFKA (+ study plans) → Landing (+3D) → Auth → Progress & Settings.

## 4. Recommended dependencies

| Package | Decision | Why / cost |
|---|---|---|
| `gsap` (incl. ScrollTrigger) | **Add** | The brief's primary motion engine; timelines, staggers, scroll reveals and reliable cleanup via `gsap.context`. Free for commercial use since 30 Apr 2025, plugins included (licence owned by Webflow). ≈ 25–30 KB gzip core + ≈ 12 KB ScrollTrigger, imported only where used. |
| `three` | **Add, landing only** | One hero scene, loaded with `import()` after first paint — not part of the app bundle. ≈ 120–150 KB gzip in its own chunk. |
| Vue Bits (official Vue port of React Bits) | **Don't add** | Licensed MIT + Commons Clause; effects are copied in per component anyway. We adapt the relevant ideas (count-up, spotlight cards, text reveal, typing indicator) as our own small components so they match Paper & Ink. |
| Taste Skill | **Optional, not needed** | A third-party pack of prompt instructions (not tooling). `docs/DESIGN.md` already fixes the art direction; installing it would mainly change *my* defaults. Happy to install it if you want. |
| Unsloth | **Out of scope** | Model-training infrastructure, not UI. |
| Smooth-scroll libraries (e.g. Lenis), extra animation libs | **Don't add** | Hijacked scrolling hurts accessibility; GSAP + CSS cover everything. |

## 5. Performance considerations

- **Budget:** app shell JS may grow by at most ~40 KB gzip (GSAP); Three.js never loads inside the app.
  Sizes recorded before/after each stage from `vite build`.
- **Animations:** transform/opacity only; no layout-thrashing properties; staggers capped; ScrollTriggers created in
  `useMotion` so route changes can't leak them.
- **WebGL:** device-pixel-ratio capped at 1.5; point count fixed; render loop stops when the hero is off-screen
  (`IntersectionObserver`) or the tab is hidden; fallback image when WebGL is unavailable.
- **No continuous loops** elsewhere — the assistant mark animates only while a reply streams.
- **Reduced motion:** every GSAP setup has a no-motion branch; content is never hidden waiting for an animation
  (initial state set by JS, so no-JS/no-motion users see everything).

## 6. Implementation sequence (each stage built, browser-checked on desktop + mobile, then committed on request)

| Stage | Work | Verified by |
|---|---|---|
| 1 — Foundation | Fix theme flash; add GSAP + `src/motion/`; tokens (elevation, data cyan); route transitions; toasts | build sizes, reload on every route (no flash), reduced-motion run |
| 2 — Components | `KCountUp`, `KProgressRing`, `KStatCard`, `KTrackCard`, `KCopyButton`, `KAssistantMark` | each used on a real page with real data |
| 3 — Dashboard | Welcome + daily objective, animated stats, four track cards, heatmap (real activity), interactive daily plan, recent activity | API data only; empty-state account + active account |
| 4 — Practice & questions | Topic cards with rings, filter transitions, completion animation, MCQ feedback/explanation transitions, position indicator, core CS reading layout | answer flows, keyboard-only pass |
| 5 — Ask KAFKA | Identity mark, thinking indicator, message entrance, copy code, polished suggestion chips, study-plan pages | live Groq stream + offline mode |
| 6 — Landing & auth | Three.js hero (lazy, fallback), scroll storytelling with ScrollTrigger, refined auth split screen | Lighthouse-style checks, WebGL-off fallback |
| 7 — Progress & settings | Charts animate on reveal, settings polish | — |
| 8 — QA | All routes, auth flows, API calls, console errors, mobile/tablet, reduced motion, production build | report |

## 7. Stage log

### Stage 1 — Foundation (done)

- **Theme flash fixed.** `index.html` paints the right surface before the app loads (public pages Paper, `/status`
  Ink, app pages the theme stored by `App.vue` in `localStorage` `kafka:theme`, default Ink); `App.vue` no longer
  writes a surface before the first navigation resolves; the body colour transition (which hid text) was removed.
  Verified by hard-reloading practice, question and Ask KAFKA: solid Ink before mount, no Paper frame.
- **GSAP 3.15.1** added (standard no-charge licence, 0 vulnerabilities). `src/motion/`: `gsap.js` (defaults,
  `prefersReducedMotion`, on-demand `loadScrollTrigger()`), `useMotion` (gsap.matchMedia + context, reverted on
  unmount, optional re-run on data), `useCountUp`, `v-reveal` (registered globally; one shared
  IntersectionObserver instead of ScrollTrigger — kept ScrollTrigger out of the app bundle).
- **Tokens:** `text-signal`/`bg-signal` (cyan for second data series; 6:1 on Paper), `shadow-elevated` /
  `shadow-elevated-hover`, and the `k-lift` utility (2 px lift on hover *and* keyboard focus).
- **Page transitions:** app pages rise in (280 ms, transform/opacity); leaving pages go instantly, so there is no
  overlap or scroll jump; re-used pages (next question, another conversation) don't re-animate.
- **Toasts:** `useToast()` + `<KToaster>` (polite/assertive live regions, pause on hover/focus, keyboard dismiss,
  max 4). Wired to: study-plan item save failure, plan deleted / delete failure, conversation deleted / delete failure
  (that path previously had no error handling).
- **Bundle:** app shell JS 42.3 → 73.0 KB gzip (+30.7 KB, budget 40); CSS 9.6 → 10.0 KB gzip; chat chunk unchanged.
- `useMotion`, `useCountUp` and `v-reveal` were first exercised in Stage 2 (below).

### Stage 2 — Components (done)

- **`KCountUp` / `KStatCard`** (replaces `KStat`): dashboard stats count up to the real `/progress/summary/` values;
  screen readers get only the final value. Verified: 16 / 18 / 67 % / 01 for a seeded account, sampled 00→02→05→09→12→16.
- **`KProgressRing`**: SVG ring sweeping via a CSS `stroke-dashoffset` transition (no animation loop). Verified the
  final offset matches 12/210.
- **`KTrackCard`** on Prepare: whole-card link, ring with real progress, `k-lift` on hover and focus, staggered
  entrance through `useMotion` (cards fade in 120 ms apart and settle at opacity 1, no transform). Topic sections use
  `v-reveal` (hidden → revealed on scroll, inline styles cleared afterwards).
- **`KCopyButton`** for solutions; markdown code fences (chat answers, explanations, statements) now render a
  language bar with a Copy button handled by one delegated listener — works while a reply streams. The fence label
  (from model output) is restricted to `[\w+#.-]`; DOMPurify still sanitises everything. Verified on a live Groq reply.
- **`KAssistantMark`**: 3×3 "K" mark in chat messages, the Ask KAFKA header and the question drawer; animates only while
  a reply streams (verified active → idle, no animation when idle). Replaces the thinking dots ("Thinking…" label).
- **Bugs fixed during verification:**
  1. GSAP and `k-lift` both drove `transform` on the same element → cards stuck mid-entrance. Rule: animate a
     wrapper (documented in `useMotion`).
  2. A paused `gsap.from` doesn't apply its start state → sections would flash, vanish, fade in. `v-reveal` now uses
     `gsap.set` on mount + `gsap.to` on intersection.
- **Bundle:** app shell 73.3 KB gzip (+0.3 KB vs Stage 1); chat chunk 74.8 KB (+0.7 KB).
- Testing note: when the browser pane is hidden, `requestAnimationFrame` and IntersectionObserver don't run at all —
  front the tab before checking animations.

### Stage 3 — Dashboard (done)

Same APIs as before plus `/topics/` (already public to the app); no backend changes. Nothing is invented.

- **Welcome hero** (`WelcomeHero`): greeting lines rise in from a mask (GSAP via `useMotion`), date, a message
  that adapts (new user / questions left / goal done), and **Today's objective** — the daily goal as a ring
  (`completed_today / items`) with the next unfinished plan item and a *Continue* link straight to it; streak badge.
- **Stats:** Stage 2 count-up cards.
- **Your tracks** (`TrackOverview`): Coding, Quantitative, Logical, Verbal and Core CS as compact `KTrackCard`s —
  aptitude split by section by summing per-topic progress; each links to the first unfinished topic. 5 columns on
  desktop, 3 on tablet, 2 on phones.
- **Activity** (`ActivityPanel`): 90-day heatmap (larger 16 px cells) that is now explorable — one tab stop, arrow
  keys move by day/week, Home/End, hover/click select — with an `aria-live` readout (questions, completed, answers);
  plus this week's questions, active days and 90-day completions (count-up).
- **Today's plan**, **Recommended next** (cards with progress rings + `k-lift`), **Recently attempted**; panels
  reveal on scroll.
- Removed the now-unused `WeeklyActivity` and `CategoryProgress`.
- **Verified** with a brand-new account (all empty states) and a seeded active account (26/28/67 %/02 best 10,
  4/5 today, 60 days of history) at 1280 px and 375 px; heatmap keyboard navigation checked (←, ↑, Home, End).
- **Bundle:** dashboard chunk 13.1 KB (4.7 KB gzip); app shell unchanged.

### Stage 4 — Practice & question pages (done)

- **One additive API change:** `GET /questions/{slug}/` → `navigation` now also returns `position` and `total`
  (curriculum order within the topic). Existing fields unchanged; test updated.
- **Practice:** each topic in the sidebar shows a 14 px progress ring (decorative — the count is text); result rows
  rise in with a quick stagger (`k-rise-quick`, 28 ms steps, capped) and replay whenever filters change the list.
- **Question page:** "Question 07 / 50" with a thin position bar and previous/next buttons beside the breadcrumb;
  Approach / Solution / Model answer panels open and close smoothly (grid rows 0fr → 1fr) and are `inert` while
  closed, so their 11 controls are out of the tab order.
- **MCQ feedback:** at the moment of answering, the correct option pops and a wrong pick shakes; the verdict and
  explanation rise in. Re-opening an answered question doesn't replay it.
- **Completion:** when an action on the page completes the question (Mark as solved, or a correct MCQ), the status
  square pops with a fading accent ring and a toast confirms it — never on simply opening a completed question.
- **Core CS reading:** concept pages cap prose at 60ch.
- **Verified** (functional; animations fast-forwarded because the pane was hidden): position/prev/next on a coding
  question (05 / 15) and concept page (01 / 10), panel inert/expanded states, Mark as solved → toast + pop,
  re-open → none, MCQ wrong → shake + "Not quite." + no toast, reset → classes cleared, correct → pop + toast,
  keyboard tab order on a coding question, phone layout (no sideways scroll).
- **Bundle:** question chunk 8.6 KB gzip, practice 4.8 KB; app shell +0.03 KB.

### Stage 5 — Ask KAFKA & study plans (done)

Frontend only; existing AI service, streaming and APIs unchanged.

- **Message entrance:** messages added during the session rise in (`TransitionGroup`); the list is keyed per
  conversation, so loaded history appears at once (verified: 0 entrance animations on reload). Also in the
  question drawer.
- **Question context card:** a conversation about a question shows what KAFKA is looking at — title, type, topic,
  difficulty and the student's status (from `GET /questions/{slug}/`, read-only) — linking back to the question.
- **Suggestions:** chips with a kind tag; the first two are built from the student's real recommended topics
  (`/progress/plan`), topped up with general ones; staggered entrance and `k-lift`.
- **Copy reply** under each finished KAFKA message (`KCopyButton` gained an `inline` variant).
- **Study plans:** generating state shows KAFKA's active mark, the current stage and four stage bars; plan phases
  reveal on scroll; ticking an item pops its checkbox.
- **Verified:** personal suggestions (Arrays, Percentages for the seeded account), context card (Merge Overlapping
  Intervals · Arrays · Medium · In progress), a live Groq hint (streamed, escalated to "Hint 2 of 3", Copy reply
  shown), history reload without animation, plan item tick (1/4, pop), generating state (request intercepted to
  avoid spending Groq quota), phone layout. Offline (`fake`) mode wasn't re-run — it would need a server restart.
- **Bundle:** Ask KAFKA chunk 4.5 KB gzip; chat chunk 75.4 KB (+0.5); app shell unchanged.
