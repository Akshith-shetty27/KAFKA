"""
Study-plan generation: pasted job description → validated, stored plan.

    clean_jd_text()     normalise the pasted text and trim it to the model budget
    generate_plan()     one structured LLM call → validate_plan() → save
    validate_plan()     enforce what the schema can't: evidence really comes from
                        the JD, links name real catalog rows, sane sizes and hours
    set_item_completed()  progress on a plan

The model's output is never trusted as-is: anything that fails validation is
dropped or clamped, and a plan without real, evidenced requirements is
rejected instead of being stored as a generic plan.
"""

import logging
import re
import unicodedata
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.assistant.llm import LLMError, get_provider
from apps.catalog.models import Pattern, Topic

from . import prompts
from .models import PlanItem, PlanPhase, PreparationPlan
from .schema import CATEGORY_VALUES, IMPORTANCE_VALUES, PHASE_KINDS, plan_schema

logger = logging.getLogger(__name__)

MAX_REQUIREMENTS = 15
MAX_PHASES = 6
MAX_ITEMS_PER_PHASE = 6
MAX_LIST_ENTRIES = 8
MIN_REQUIREMENTS = 2


class PlanRejected(Exception):
    """The input can't be turned into a JD-specific plan (shown to the student, not retryable)."""


# --- input -------------------------------------------------------------------------

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_jd_text(text: str) -> tuple[str, bool]:
    """Normalise pasted text; return (text for the model, whether it was trimmed)."""
    text = unicodedata.normalize("NFKC", text).replace("\r\n", "\n").replace("\r", "\n")
    text = _CONTROL.sub("", text)
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    limit = settings.PREP_JD_PROMPT_CHARS
    if len(text) <= limit:
        return text, False
    cut = text.rfind("\n", 0, limit)
    return text[: cut if cut > limit * 0.7 else limit].rstrip(), True


def catalog_for_prompt() -> tuple[list[dict], list[dict]]:
    """Topics that have published questions, and all patterns — the only valid link targets."""
    topics = (
        Topic.objects.select_related("category")
        .annotate(n=Count("questions", filter=Q(questions__is_published=True)))
        .filter(n__gt=0)
        .order_by("category__order", "order")
    )
    patterns = Pattern.objects.order_by("order", "name")
    return (
        [{"slug": t.slug, "name": t.name, "category": t.category.name} for t in topics],
        [{"slug": p.slug, "name": p.name} for p in patterns],
    )


# --- validation ----------------------------------------------------------------------


def _norm(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9+#]+", text.lower()))


def evidence_in_jd(evidence: str, jd_norm: str, jd_words: set[str]) -> bool:
    """True if the quote really comes from the JD (exact after normalising, or ≥ 80% of its words)."""
    ev = _norm(evidence)
    if len(ev) < 3:
        return False
    if ev in jd_norm:
        return True
    words = [w for w in ev.split() if len(w) >= 3]
    return bool(words) and sum(w in jd_words for w in words) / len(words) >= 0.8


def _text(value, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _str_list(value, limit: int = 160) -> list[str]:
    if not isinstance(value, list):
        return []
    out = []
    for entry in value:
        text = _text(entry, limit)
        if text and text not in out:
            out.append(text)
    return out[:MAX_LIST_ENTRIES]


def _known(value, allowed: set[str]) -> list[str]:
    """Catalog links: only slugs that really exist, de-duplicated, in the model's order."""
    if not isinstance(value, list):
        return []
    slugs = (str(v).strip().lower() for v in value)
    return [s for s in dict.fromkeys(slugs) if s in allowed][:MAX_LIST_ENTRIES]


def _choice(value, allowed: list[str], default: str) -> str:
    value = str(value or "").strip().lower().replace(" ", "_").replace("-", "_")
    return value if value in allowed else default


def _hours(value) -> Decimal:
    try:
        hours = float(value)
    except (TypeError, ValueError):
        hours = 2.0
    hours = min(40.0, max(0.5, hours))
    return Decimal(str(round(hours * 2) / 2))  # nearest half hour


def validate_plan(
    data: dict, *, jd_text: str, topic_slugs: set[str], pattern_slugs: set[str], hours_budget: int | None = None
) -> dict:
    """Turn a model reply into a clean plan dict, or raise PlanRejected.

    With `hours_budget`, item hours are scaled so the plan fits the student's
    time (models estimate totals loosely; measured drift was up to ±40%).
    """
    if data.get("is_job_description") is False:
        reason = _text(data.get("rejection_reason"), 300) or "It doesn't describe a role's responsibilities and requirements."
        raise PlanRejected(f"That doesn't look like a job description. {reason}")

    jd_norm = _norm(jd_text)
    jd_words = set(jd_norm.split())
    requirements, seen = [], set()
    for req in data.get("requirements") or []:
        if not isinstance(req, dict):
            continue
        skill = _text(req.get("skill"), 120)
        evidence = _text(req.get("evidence"), 300)
        if not skill or skill.lower() in seen or not evidence_in_jd(evidence, jd_norm, jd_words):
            continue
        seen.add(skill.lower())
        requirements.append(
            {
                "skill": skill,
                "category": _choice(req.get("category"), CATEGORY_VALUES, "domain"),
                "importance": _choice(req.get("importance"), IMPORTANCE_VALUES, "medium"),
                "evidence": evidence,
            }
        )
    if len(requirements) < MIN_REQUIREMENTS:
        raise PlanRejected(
            "KAFKA couldn't find clear requirements in that text. Paste the full job description, "
            "including the responsibilities and required skills."
        )
    rank = {"high": 0, "medium": 1, "low": 2}
    requirements.sort(key=lambda r: rank[r["importance"]])  # stable: keeps the model's order within a level

    phases = []
    for phase in data.get("phases") or []:
        if not isinstance(phase, dict):
            continue
        kind = _choice(phase.get("kind"), PHASE_KINDS, "technical")
        items = []
        for item in phase.get("items") or []:
            if not isinstance(item, dict) or not _text(item.get("title"), 200):
                continue
            items.append(
                {
                    "title": _text(item.get("title"), 200),
                    "category": _choice(item.get("category"), CATEGORY_VALUES, "domain"),
                    "importance": _choice(item.get("importance"), IMPORTANCE_VALUES, "medium"),
                    "reason": _text(item.get("reason"), 600),
                    "subtopics": _str_list(item.get("subtopics")),
                    "activities": _str_list(item.get("activities"), 240),
                    "est_hours": _hours(item.get("est_hours")),
                    "topics": _known(item.get("topics"), topic_slugs),
                    "patterns": _known(item.get("patterns"), pattern_slugs),
                }
            )
            if len(items) == MAX_ITEMS_PER_PHASE:
                break
        if items:
            phases.append(
                {
                    "kind": kind,
                    "title": _text(phase.get("title"), 160) or PlanPhase.Kind(kind).label,
                    "goal": _text(phase.get("goal"), 400),
                    "items": items,
                }
            )
    phases.sort(key=lambda p: PHASE_KINDS.index(p["kind"]))  # stable
    phases = phases[:MAX_PHASES]
    if not phases:
        raise PlanRejected("KAFKA couldn't build a roadmap from that description. Please try again with the full text.")
    if hours_budget:
        _fit_to_budget(phases, Decimal(hours_budget))

    return {
        "summary": _text(data.get("summary"), 1200),
        "requirements": requirements[:MAX_REQUIREMENTS],
        "phases": phases,
    }


def _fit_to_budget(phases: list[dict], budget: Decimal) -> None:
    items = [item for phase in phases for item in phase["items"]]
    total = sum(item["est_hours"] for item in items)
    if total and abs(total - budget) > budget * Decimal("0.1"):
        factor = budget / total
        for item in items:
            item["est_hours"] = _hours(float(item["est_hours"] * factor))


# --- generation ------------------------------------------------------------------------


def generate_plan(
    user, *, role: str, job_description: str, company: str = "", candidate_info: str = "",
    days_available: int | None = None, hours_per_day: int | None = None,
) -> PreparationPlan:
    """Generate, validate and store a plan. Raises PlanRejected or LLMError."""
    provider = get_provider()
    if not provider.configured:
        raise LLMError("ASK KAFKA isn't configured yet (no API key on the server).", retryable=False)

    jd_text, truncated = clean_jd_text(job_description)
    topics, patterns = catalog_for_prompt()
    if days_available and not hours_per_day:
        hours_per_day = 2

    prompt = prompts.user_prompt(
        role=role, company=company, candidate_info=candidate_info, days_available=days_available,
        hours_per_day=hours_per_day, jd_text=jd_text, topics=topics, patterns=patterns,
    )
    data, result = provider.complete_json(
        system=prompts.SYSTEM,
        prompt=prompt,
        schema=plan_schema(),
        name="study_plan",
        max_tokens=settings.PREP_PLAN_MAX_TOKENS,
        effort=settings.PREP_LLM_EFFORT,
    )
    logger.info(
        "Study plan generated (model=%s, in=%s, out=%s tokens)", result.model, result.input_tokens, result.output_tokens
    )
    clean = validate_plan(
        data, jd_text=jd_text,
        topic_slugs={t["slug"] for t in topics}, pattern_slugs={p["slug"] for p in patterns},
        hours_budget=days_available * hours_per_day if days_available else None,
    )
    return _save(
        user, clean, role=role, company=company, job_description=job_description, truncated=truncated,
        candidate_info=candidate_info, days_available=days_available, hours_per_day=hours_per_day,
        provider=provider.name, result=result,
    )


@transaction.atomic
def _save(user, clean, *, role, company, job_description, truncated, candidate_info, days_available,
          hours_per_day, provider, result) -> PreparationPlan:
    plan = PreparationPlan.objects.create(
        user=user, role=role, company=company, job_description=job_description, jd_truncated=truncated,
        candidate_info=candidate_info, days_available=days_available, hours_per_day=hours_per_day,
        summary=clean["summary"], requirements=clean["requirements"],
        provider=provider, model=result.model, input_tokens=result.input_tokens, output_tokens=result.output_tokens,
    )
    topic_ids = dict(Topic.objects.values_list("slug", "id"))
    pattern_ids = dict(Pattern.objects.values_list("slug", "id"))
    for p_order, phase in enumerate(clean["phases"], 1):
        row = PlanPhase.objects.create(plan=plan, order=p_order, kind=phase["kind"], title=phase["title"], goal=phase["goal"])
        for i_order, item in enumerate(phase["items"], 1):
            plan_item = PlanItem.objects.create(
                phase=row, order=i_order, title=item["title"], category=item["category"],
                importance=item["importance"], reason=item["reason"], subtopics=item["subtopics"],
                activities=item["activities"], est_hours=item["est_hours"],
            )
            plan_item.topics.set([topic_ids[s] for s in item["topics"]])
            plan_item.patterns.set([pattern_ids[s] for s in item["patterns"]])
    return plan


# --- progress ----------------------------------------------------------------------------


def set_item_completed(item: PlanItem, completed: bool) -> PlanItem:
    if completed and item.completed_at is None:
        item.completed_at = timezone.now()
    elif not completed:
        item.completed_at = None
    item.save(update_fields=["completed_at"])
    PreparationPlan.objects.filter(pk=item.phase.plan_id).update(updated_at=timezone.now())
    return item


def check_plan_input(job_description: str) -> None:
    """Input checks that need settings (kept out of the serializer so tests can override them)."""
    length = len(job_description.strip())
    if length < settings.PREP_JD_MIN_CHARS:
        raise ValidationError(
            {"job_description": [f"Paste the full job description (at least {settings.PREP_JD_MIN_CHARS} characters)."]}
        )
    if length > settings.PREP_JD_MAX_CHARS:
        raise ValidationError(
            {"job_description": [f"That's too long — keep it under {settings.PREP_JD_MAX_CHARS:,} characters."]}
        )
