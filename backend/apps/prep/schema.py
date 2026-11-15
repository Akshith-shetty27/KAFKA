"""
The JSON Schema the model must answer in.

Topic/pattern links are plain strings checked against the catalog afterwards.

Written for strict structured outputs (Groq / OpenAI-style): every object
lists all of its properties as required and forbids extra ones. Limits that
strict mode can't express (list lengths, hour ranges) are enforced afterwards
by `services.validate_plan`.
"""

from .models import Importance, PlanPhase, SkillCategory

CATEGORY_VALUES = [c.value for c in SkillCategory]
IMPORTANCE_VALUES = [c.value for c in Importance]
PHASE_KINDS = [c.value for c in PlanPhase.Kind]


def _obj(**properties) -> dict:
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


def _str(description: str) -> dict:
    return {"type": "string", "description": description}


def _enum(values: list[str], description: str) -> dict:
    return {"type": "string", "enum": values, "description": description}


def _str_list(description: str) -> dict:
    return {"type": "array", "items": {"type": "string"}, "description": description}


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
    item = _obj(
        title=_str("What to study, e.g. 'Hash maps and frequency counting'."),
        category=_category(),
        importance=_enum(IMPORTANCE_VALUES, "Priority for this candidate and this job."),
        reason=_str("At most 30 words tying this item to specific requirements in the job description."),
        subtopics=_str_list("2–5 concrete subtopics (a few words each)."),
        activities=_str_list("2–3 concrete things to do, e.g. 'Solve 6 medium sliding-window problems'."),
        est_hours=_num("Estimated hours for this item (0.5–40)."),
        topics=_slug_list("Slugs of KAFKA practice topics that train this item, from the list provided (may be empty)."),
        patterns=_slug_list("Slugs of KAFKA coding patterns that train this item, from the list provided (may be empty)."),
    )
    phase = _obj(
        kind=_enum(PHASE_KINDS, "Phase type; phases appear in this order."),
        title=_str("Short phase title."),
        goal=_str("What the candidate can do by the end of this phase."),
        items={"type": "array", "items": item, "description": "2–4 items, highest priority first."},
    )
    return _obj(
        is_job_description=_bool("False if the text is not a job description or posting."),
        rejection_reason=_str("If is_job_description is false, a short reason; otherwise an empty string."),
        summary=_str("2–3 sentences: what this role needs and where the preparation should focus."),
        requirements={"type": "array", "items": requirement, "description": "The 6–12 most important requirements."},
        phases={"type": "array", "items": phase, "description": "3–5 phases in preparation order."},
    )


def _num(description: str) -> dict:
    return {"type": "number", "description": description}


def _bool(description: str) -> dict:
    return {"type": "boolean", "description": description}
