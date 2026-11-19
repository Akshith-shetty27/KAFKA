# Decision map
repo: KAFKA | built from: b670c7e | date: 2026-11-19
root problem: I wanted to build a one-stop solution where students can come and prepare for all the interview-related topics, like aptitude, coding questions, core CS, and all that, so they don't need to go through multiple websites. I wanted to make students' lives simpler and help them prepare more efficiently and in a structured way.

## D1. Bring different kinds of interview practice into one place
- Problem: Students need to prepare across aptitude, coding and core CS without going to multiple websites.
- Given: The product must offer material grouped into useful subjects and support browsing and practice.
- Constraints, in order:
  1. The material has different formats and overlaps in useful ways -> breaks: treating the whole bank as one undifferentiated list.
- Decision: normalized content catalog, categories and topics organize questions while related records carry type-specific details.
- Options: one flat list; separate unrelated banks per subject; shared category-topic-question catalog with related details (real). A shared catalog enables unified browsing; separate banks can fit each subject but make cross-track product flows harder.
- Evidence: commit 91b53aa, files backend/apps/catalog/models.py, backend/apps/catalog/content/, backend/apps/catalog/management/commands/seed_content.py.

## D2. Keep each student's preparation state private
- Problem: Students need accounts, and one student's work must never appear to another.
- Given: Browser clients call a shared server backed by a relational database.
- Constraints, in order:
  1. Every read and write is scoped to the signed-in student -> breaks: globally queried progress rows.
- Decision: user-scoped persistence, every owned record and query tied to its student.
- Options: per-user database; tenant key on owned records (real); separate database per student. Shared DB is easy to operate; isolated DBs provide stronger separation but add cost and complexity.
- Evidence: commit 91b53aa, files backend/apps/accounts/models.py, backend/apps/progress/selectors.py, backend/apps/prep/selectors.py; code only.

## D3. Make practice state useful for both current status and history
- Problem: A student needs to know what's done and see activity over time.
- Given: Question interactions can repeat and analytics need dates, outcomes and streaks.
- Constraints, in order:
  1. Current completion should be cheap to read while every interaction remains countable -> breaks: deriving all status from an event log or overwriting history with a status flag.
- Decision: state plus append-only activity log, one current progress row alongside dated events.
- Options: current-state rows only; events only; both (real). Both makes dashboards direct while preserving history, at the cost of maintaining two related representations.
- Evidence: commit 91b53aa, files backend/apps/progress/models.py, backend/apps/progress/services.py, backend/apps/progress/selectors.py; docs/ARCHITECTURE.md.

## D4. Connect a student's browser to protected backend operations
- Problem: Students need private accounts and a frontend that can call the API without exposing long-lived credentials.
- Given: A Vue single-page app and Django API communicate over HTTP.
- Constraints, in order:
  1. A page reload must restore a session while browser scripts should not read the long-lived credential -> breaks: storing both credentials in browser-accessible state.
- Decision: short-lived in-memory access token plus httpOnly refresh cookie, rotated by the API.
- Options: server session; both tokens in local storage; access in memory and refresh in httpOnly cookie (real). Cookie reduces script access; refresh flow adds coordination and failure handling.
- Evidence: commit 91b53aa, files backend/apps/accounts/cookies.py, backend/apps/accounts/services.py, frontend/src/services/http.js; docs/ARCHITECTURE.md.

## D5. Let an AI mentor respond while preserving a useful conversation
- Problem: Students need contextual help during practice, including hints that do not reveal answers too early.
- Given: Conversations and questions are stored locally; an external model generates text.
- Constraints, in order:
  1. The model may be unavailable or stop mid-reply -> breaks: treating every request as an all-or-nothing response.
  2. A hint must not leak a solution before the student completes the question -> breaks: sending the full question record as context.
- Decision: provider adapter plus streamed, persisted turns; build context according to mode and reveal state.
- Options: call a provider directly inside the HTTP view; adapter and service generator (real); queue jobs and poll. Streaming gives immediate feedback; persistence of partial replies preserves continuity.
- Evidence: commit 5941f8c, files backend/apps/assistant/services.py, backend/apps/assistant/context.py, backend/apps/assistant/llm/; docs/PROGRESS.md.

## D6. Turn a job description into a usable preparation roadmap
- Problem: Generic practice does not tell a student what to prioritize for a specific role.
- Given: A pasted job description, an LLM and an existing topic catalog.
- Constraints, in order:
  1. Recommendations must be traceable to the JD and actionable in the existing product -> breaks: saving raw model output as trusted plan data.
  2. The model may invent catalog links or unsupported requirements -> breaks: trusting structurally valid JSON alone.
- Decision: structured generation followed by evidence and catalog validation before saving linked plan records.
- Options: free-form chat response; persist structured model output directly; schema-constrained output with application validation (real). Validation costs code but makes roadmap claims and links checkable.
- Evidence: commit f111339, files backend/apps/prep/services.py, backend/apps/prep/schema.py, backend/apps/prep/prompts.py; docs/PROGRESS.md.

## D7. Expand a large bank without hand-writing every item
- Problem: Each topic needs enough varied questions to support repeated preparation.
- Given: Content is authored as reviewable Python data and loaded into relational tables.
- Constraints, in order:
  1. Generated quantitative questions need answers that can be checked, and duplicates should be rejected -> breaks: unconstrained LLM-generated questions.
- Decision: parameterized authoring-time generators with recomputed answers and seeded content.
- Options: write every item manually; generate all text with an LLM; parameterized templates/rules converted into ordinary content (real). Generators scale and verify numeric keys, while authored verbal items retain editorial control.
- Evidence: commit f8ac9cd, files backend/apps/catalog/content/generators/, backend/apps/catalog/management/commands/generate_aptitude.py; docs/PLAN-V2.md.
