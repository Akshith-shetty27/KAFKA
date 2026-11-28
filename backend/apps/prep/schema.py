"""
JSON Schemas the model must answer in: the study plan, and an on-demand lesson.

Topic/pattern links are plain strings checked against the catalog afterwards.

Written for strict structured outputs (Groq / OpenAI-style): every object
lists all of its properties as required and forbids extra ones. Limits that
strict mode can't express (list lengths, hour ranges, which links fit which
section) are enforced afterwards by `services.validate_plan` /
`services.validate_lesson`.
"""

from .models import Importance, PlanItem, SkillCategory

CATEGORY_VALUES = [c.value for c in SkillCategory]
IMPORTANCE_VALUES = [c.value for c in Importance]
# Sections of a plan, in display order: KAFKA's three tracks, then interview prep.
SECTION_KINDS = ["coding", "aptitude", "core_cs", "interview"]
MODE_VALUES = [m.value for m in PlanItem.Mode]
BASIS_VALUES = ["company", "similar", "none"]


def _obj(**properties) -> dict:
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


def _str(description: str) -> dict:
    return {"type": "string", "description": description}


def _enum(values: list[str], description: str) -> dict:
    return {"type": "string", "enum": values, "description": description}


def _str_list(description: str) -> dict:
    return {"type": "array", "items": {"type": "string"}, "description": description}


def _num(description: str) -> dict:
    return {"type": "number", "description": description}


def _bool(description: str) -> dict:
    return {"type": "boolean", "description": description}


def _slug_list(description: str) -> dict:
    # Deliberately not an enum: Groq validates enums only after generation and
    # rejects the whole reply on one bad slug. Unknown slugs are dropped by
    # services.validate_plan instead.
    return {"type": "array", "items": {"type": "string"}, "description": description}


def _category() -> dict:
    choices = "; ".join(f"{c.value} ({c.label})" for c in SkillCategory)
    return _str(f"Kind of skill — exactly one of these values: {choices}.")


def plan_schema() -> dict:
    requirement = _obj(
        skill=_str("A specific skill or knowledge area the job asks for, e.g. 'REST API design' or 'SQL joins'."),
        category=_category(),
        importance=_enum(IMPORTANCE_VALUES, "How strongly the job description emphasises it."),
        evidence=_str("A short phrase copied word for word from the job description that shows this requirement."),
    )
    round_ = _obj(
        name=_str("Round name, e.g. 'Online assessment' or 'Technical interview 1'."),
        details=_str("At most 25 words: what is asked in this round."),
    )
    research = _obj(
        company_found=_str("The company the interview reports are actually about, or '' if none were found."),
        basis=_enum(BASIS_VALUES, "company: reports are about this exact company; similar: about similar companies "
                    "for this role; none: no usable research."),
        summary=_str("1–2 sentences on how this company (or similar ones) interviews for the role; '' if none."),
        rounds={"type": "array", "items": round_, "description": "The interview rounds in order (0–6)."},
        frequently_asked=_str_list("Up to 8 topics most often asked, a few words each."),
    )
    item = _obj(
        title=_str("What to prepare, e.g. 'Hash maps and frequency counting'."),
        mode=_enum(MODE_VALUES, "practice: KAFKA topics/patterns cover it (link them); lesson: KAFKA's question "
                   "bank doesn't cover it, so KAFKA will teach it with notes and a quiz; mock: an interview round "
                   "to rehearse with an Ask KAFKA mock interview."),
        category=_category(),
        importance=_enum(IMPORTANCE_VALUES, "Priority for this candidate and this job."),
        reason=_str("At most 30 words tying this item to the job description and/or the interview research."),
        subtopics=_str_list("2–5 concrete subtopics (a few words each)."),
        est_hours=_num("Estimated hours for this item (0.5–40)."),
        topics=_slug_list("Slugs of KAFKA practice topics from this section's track that train this item (may be empty)."),
        patterns=_slug_list("Slugs of KAFKA coding patterns that train this item — coding section only (may be empty)."),
    )
    section = _obj(
        kind=_enum(SECTION_KINDS, "coding, aptitude, core_cs or interview; each at most once."),
        goal=_str("What the candidate can do by the end of this section."),
        items={"type": "array", "items": item, "description": "2–4 items, highest priority first."},
    )
    return _obj(
        is_job_description=_bool("False if the text is not a job description or posting."),
        rejection_reason=_str("If is_job_description is false, a short reason; otherwise an empty string."),
        summary=_str("2–3 sentences: what this role needs and where the preparation should focus."),
        research=research,
        requirements={"type": "array", "items": requirement, "description": "The 6–12 most important requirements."},
        sections={"type": "array", "items": section, "description": "The sections this job needs, 2–4 of them."},
    )


def lesson_schema() -> dict:
    question = _obj(
        question=_str("A multiple-choice question testing one idea from the notes."),
        options={"type": "array", "items": {"type": "string"}, "description": "Exactly 4 short options."},
        answer=_num("Index (0–3) of the correct option."),
        explanation=_str("At most 30 words: why that option is right."),
    )
    section = _obj(
        heading=_str("Short heading."),
        body=_str("60–120 words of clear explanation, plain text (no links, no markdown headings)."),
    )
    return _obj(
        sections={"type": "array", "items": section, "description": "3–5 sections, basics first."},
        key_points=_str_list("4–6 one-line points to remember for the interview."),
        quiz={"type": "array", "items": question, "description": "5 questions."},
    )
