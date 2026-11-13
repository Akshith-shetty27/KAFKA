# KAFKA — Design Direction

Status: **Approved and implemented** (Phase 3). Tokens live in `frontend/src/assets/styles/main.css`.

Source material: the four reference screenshots (landing hero, "The KAFKA Method",
feature trio, "Show up. Get sharper. Go further.") plus the written brief.

---

## 1. What the references actually do

| Aspect | Observation | Rule we derive |
|---|---|---|
| Canvas | Warm off-white "paper" (`~#FFFCF2`), not pure white. | Never use `#FFF` as a page background. |
| Contrast blocks | Full-bleed **pure black** sections and panels interrupt the paper. | Dark is used as *emphasis*, not as decoration. |
| Accent | One accent only: **electric teal** (`~#22DCC8`). Used for streaks, completed states, one word per headline, charts. | Accent ≤ ~5% of any screen. Never a gradient. |
| Display type | Huge, tightly tracked, uppercase neo-grotesk ("YOUR NEXT", "STARTS HERE."). | Display sizes only on landing/section openers, never in data UI. |
| Contrast type | High-contrast **italic serif** for one phrase per headline ("*BIG THING*", "*REIMAGINED.*") and for numerals ("*07*"). | Serif italic = emotion/emphasis. Max one serif phrase per heading. |
| Labels | Monospace, uppercase, very wide tracking ("INTERVIEW PREPARATION / 001"). Numbered sections. | Every section opens with a mono eyebrow + index. |
| Body | Clean geometric sans (DM Sans-like), generous line-height, muted grey for secondary text. | Body 16–18px, 1.6 line-height, max ~65ch. |
| Links / CTAs | Text + `↗` arrow with a 1px underline, wide tracking. No pill buttons. | Primary CTA is an underlined text-link; filled buttons only inside forms/app actions. |
| Structure | Hairline 1px rules, numbered columns (01/02/03), lots of whitespace, hard edges (no border-radius). | Rules instead of card shadows; radius 0 (2px max on inputs). |
| Iconography | Typographic glyphs instead of icons: `{ }`, `Σ`, `◎`. | Categories are represented by serif glyphs, not icon packs. |
| "Tech" texture | Black panel with a faint square grid, a tilted code window with mac traffic lights, "12 tests passed". | The grid texture is our "futuristic" signal. |
| Data viz | Flat teal bars, mono day labels (M T W T F S S), serif italic big number. | Charts are hand-built SVG/CSS, single-hue, no axes clutter. |

## 2. Conflict with the written brief

The brief asks for a **"dark futuristic, space-inspired interface with subtle gradients."**
The references are a **light editorial / Swiss-brutalist** language: paper canvas, black blocks,
one flat accent, no gradients, nothing space-themed.

These are genuinely different directions. Per the visual-references instruction
("treat these references as the primary visual direction"), the references win on *language*.
The brief's "dark" requirement is satisfied by the references' own black "ink" surfaces.

### Proposed unified direction — "Paper & Ink"

One design system, two surface modes, both taken directly from the references:

- **Paper** — cream canvas, black ink, teal accent. Used for marketing and reading-heavy pages.
- **Ink** — black canvas with the faint grid, off-white text, same teal. This is the "dark futuristic" mode.

| Area | Default surface | Why |
|---|---|---|
| Landing | Paper with Ink sections (exactly like the references) | Matches the screenshots 1:1 in language. |
| Login / Register | Split: Paper form + Ink side panel (code window + streak) | Reuses the hero's panel. |
| Authenticated app (dashboard, practice, Ask KAFKA, analytics, profile) | **Ink by default**, user can switch to Paper in Settings | Satisfies the brief's dark requirement; long sessions are easier on a dark canvas. |
| Code blocks, solution panels, chat composer | Always Ink | Code reads best on dark, and it is how the references show code. |

"Space-inspired" is interpreted as the subtle grid + mono coordinates (`K / 01`) — not stars or nebula gradients,
which would clash with the references. Gradients: none.

## 3. Design tokens (to be implemented as Tailwind v4 `@theme` CSS variables)

```
Color — raw
  paper-50   #FFFCF2   page canvas (Paper)
  paper-100  #F6F2E6   subtle fills on Paper
  ink-950    #050505   page canvas (Ink)
  ink-900    #0E0E0E   raised panels on Ink
  ink-800    #1A1A1A   grid lines / hairlines on Ink
  ink-600    #3A3A3A
  stone-500  #7A776E   muted text on Paper
  stone-400  #8E8B82   muted text on Ink
  teal-400   #22DCC8   accent
  teal-500   #14BFAC   accent hover / on-paper text accent (contrast)
  signal-red #F0614A   errors, "hard" difficulty, traffic light
  signal-amb #F2B33D   warnings, "medium" difficulty, traffic light

Color — semantic (switch per mode)
  --bg, --surface, --surface-raised, --text, --text-muted,
  --rule, --accent, --accent-ink (text on accent), --danger, --warning

Type families
  display   "Inter Tight"       600, tracking -0.04em, uppercase
  serif     "Instrument Serif"  italic, for emphasis words + big numerals
  sans      "DM Sans"           400/500, body & UI
  mono      "JetBrains Mono"    400/500, eyebrows, labels, code, stats

Type scale (rem)  12 · 13 · 14 · 16 · 18 · 22 · 28 · 40 · 56 · 88 · 128
Eyebrow           mono 12–13px, uppercase, tracking 0.3em
Spacing           4px base: 4 8 12 16 24 32 48 64 96 128
Radius            0 everywhere; 2px on inputs only
Borders           1px hairlines (--rule)
Motion            150ms (hover), 250ms (panels), ease-out; respects prefers-reduced-motion
Layout            12-col grid, max-width 1280px, gutters 24px (mobile 16px)
```

Contrast note: teal `#22DCC8` on paper fails WCAG for small text, so on Paper the accent is
used for fills/bars and `teal-500`/ink is used for teal-coloured *text*. On Ink, `#22DCC8` passes.

## 4. Component inventory (reusable, `components/ui/`)

| Component | Based on |
|---|---|
| `KEyebrow` | "INTERVIEW PREPARATION / 001" mono label with index |
| `KArrowLink` | "START PREPARING ↗" underlined link (router-link or anchor) |
| `KButton` | Solid ink / solid teal / ghost; used for form submits and app actions |
| `KPanel` | Ink surface with optional grid texture (the hero panel) |
| `KRule` / numbered columns | "01 / 02 / 03" hairline feature columns |
| `KGlyph` | Serif glyph tile (`{ }`, `Σ`, `◎`) for categories |
| `KCodeWindow` | Tilted-able code window with traffic lights + status bar |
| `KChecklist` | "TODAY'S PLAN" rows with teal square checkbox + DONE/NEXT tag |
| `KBarChart` | Weekly teal bars with mono day labels |
| `KStat` | Serif italic big number + mono label ("*07* DAY STREAK") |
| `KStreakBadge` | Teal block "DAILY STREAK *07* 🔥" |
| `KDifficulty` | EASY / MEDIUM / HARD mono tag (teal / amber / red dot) |
| `KProgressBar` | 2px hairline progress, teal fill |
| `KInput`, `KSelect`, `KCheckbox`, `KTabs` | Form primitives in the same language |
| `KSkeleton`, `KEmptyState`, `KErrorState` | Loading / empty / error states |

## 5. Navigation mapping (reference nav → product)

Reference nav: `HOME · PREPARE · PRACTICE · INTERVIEW · ASK KAFKA · SETTINGS` + `START PREPARING ↗`

Implemented as: public header = in-page anchors (Method, Prepare, Ask Kafka) + Sign in + Start preparing; app header = only pages that exist (`router/navigation.js`), growing each phase.

| Nav item | Logged out | Logged in |
|---|---|---|
| HOME | Landing | Dashboard |
| PREPARE | → Register | Preparation hub: 3 categories → topics, progress per topic, today's plan |
| PRACTICE | → Register | Question library with Coding / Aptitude / Core CS tabs, filters, pagination |
| INTERVIEW | — | Renamed **PROGRESS** (analytics page, Phase 6) — decision D10 |
| ASK KAFKA | → Login | AI assistant |
| SETTINGS | — | Profile & settings (incl. Paper/Ink theme) |
| START PREPARING ↗ | Register | becomes avatar/account menu |

Mobile: nav collapses into a full-screen Ink menu with large display-type links.
