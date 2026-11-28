"""
Study-plan generation: pasted job description → web research → validated, stored plan.

    clean_jd_text()     normalise the pasted text and trim it to the model budget
    research_interviews()  web search for the company's past interview experiences
                        (best effort: a plan is still made without it)
    generate_plan()     research → one structured LLM call → validate_plan() → save
    validate_plan()     enforce what the schema can't: evidence really comes from
                        the JD, links name real catalog rows from the right track,
                        every item is doable inside KAFKA, sane sizes and hours
    generate_lesson()   notes + quiz for a lesson item, made on first open and stored
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
from .schema import BASIS_VALUES, CATEGORY_VALUES, IMPORTANCE_VALUES, SECTION_KINDS, lesson_schema, plan_schema

logger = logging.getLogger(__name__)

MAX_REQUIREMENTS = 15
MAX_ITEMS_PER_PHASE = 6
MAX_LIST_ENTRIES = 8
MIN_REQUIREMENTS = 2
MAX_ROUNDS = 6
RESEARCH_CHARS = 2000  # research report kept for the plan prompt (≈500 tokens)

# Which catalog track each section practises on (interview prep has none).
SECTION_TRACK = {"coding": "coding", "aptitude": "aptitude", "core_cs": "core-cs"}
# Item category when the model gives none we recognise.
SECTION_CATEGORY = {"coding": "dsa", "aptitude": "aptitude", "core_cs": "cs_fundamentals", "interview": "communication"}


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
    """Topics that have published questions (with their track), and all patterns — the only valid link targets."""
    topics = (
        Topic.objects.select_related("category")
        .annotate(n=Count("questions", filter=Q(questions__is_published=True)))
        .filter(n__gt=0)
        .order_by("category__order", "order")
    )
    patterns = Pattern.objects.order_by("order", "name")
    return (
        [{"slug": t.slug, "name": t.name, "track": t.category.slug} for t in topics],
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


def _norm_company(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower().replace("technologies", "").replace("limited", ""))


def validate_research(data, *, company: str, sources: list[str]) -> dict:
    """Clean the model's summary of the web research; {} when there's nothing usable."""
    if not isinstance(data, dict):
        return {}
    basis = _choice(data.get("basis"), BASIS_VALUES, "none")
    found = _text(data.get("company_found"), 120)
    if found.lower() in ("none", "n/a", "unknown"):
        found = ""
    # Reports about a differently named company are "similar", whatever the model says
    # (e.g. a search for "Wifli" that came back with "Wipfli").
    if basis == "company" and company and found:
        target, about = _norm_company(company), _norm_company(found)
        if target and about and target not in about and about not in target:
            basis = "similar"
    rounds = []
    for r in data.get("rounds") or []:
        if isinstance(r, dict) and _text(r.get("name"), 80):
            rounds.append({"name": _text(r.get("name"), 80), "details": _text(r.get("details"), 300)})
    research = {
        "company_found": found,
        "basis": basis,
        "summary": _text(data.get("summary"), 600),
        "rounds": rounds[:MAX_ROUNDS],
        "frequently_asked": _str_list(data.get("frequently_asked"), 80),
        "sources": sources,
    }
    if basis == "none" and not (research["rounds"] or research["frequently_asked"]):
        return {}
    return research


_COMMON_WORDS = {"and", "of", "the", "in", "for", "to", "a", "an", "with", "basics", "concepts", "fundamentals"}


def _topic_keys(name: str) -> tuple[str, str]:
    """('object oriented programming', 'oop') — a topic's normalised name and its acronym."""
    words = [w for w in _norm(name.replace("-", " ")).split() if w not in _COMMON_WORDS]
    return " ".join(words), "".join(w[0] for w in words) if len(words) >= 2 else ""


# The usual short names students and job posts use for core CS subjects.
TOPIC_ALIASES = {
    "database management systems": ["dbms", "rdbms", "databases"],
    "object oriented programming": ["oop", "oops"],
    "operating systems": ["os"],
    "computer networks": ["cn", "networking", "networks"],
    "software engineering": ["sdlc"],
}


def match_topics(text: str, candidates: dict[str, str]) -> list[str]:
    """Topics (slug → name) that the text names outright or by a short name — e.g. 'OOP concepts in Java'."""
    norm = f" {_norm(text)} "
    found = []
    for slug, name in candidates.items():
        full, acronym = _topic_keys(name)
        keys = [full, *TOPIC_ALIASES.get(full, [])] + ([acronym] if len(acronym) >= 2 else [])
        if any(key and f" {key} " in norm for key in keys):
            found.append(slug)
    return found


def _clean_item(item: dict, kind: str, topic_tracks: dict[str, str], pattern_slugs: set[str],
                topic_names: dict[str, str] | None = None) -> dict:
    track = SECTION_TRACK.get(kind)
    # Links must be real catalog rows from this section's track (interview prep links nothing).
    topics = [t for t in _known(item.get("topics"), set(topic_tracks)) if track and topic_tracks[t] == track]
    if track and not topics and topic_names:
        # Safety net: the model sometimes misses a KAFKA topic that the item names outright.
        in_track = {slug: name for slug, name in topic_names.items() if topic_tracks.get(slug) == track}
        topics = match_topics(" ".join([_text(item.get("title"), 200), *_str_list(item.get("subtopics"))]), in_track)
    patterns = _known(item.get("patterns"), pattern_slugs) if kind == "coding" else []
    mode = _choice(item.get("mode"), [m.value for m in PlanItem.Mode], "")
    if kind == "interview":
        mode = "lesson" if mode == "lesson" else "mock"
        topics = patterns = []
    else:
        # Everything happens inside KAFKA: with links it's practice, without them KAFKA teaches it.
        mode = "practice" if (topics or patterns) else "lesson"
    return {
        "title": _text(item.get("title"), 200),
        "mode": mode,
        "category": _choice(item.get("category"), CATEGORY_VALUES, SECTION_CATEGORY[kind]),
        "importance": _choice(item.get("importance"), IMPORTANCE_VALUES, "medium"),
        "reason": _text(item.get("reason"), 600),
        "subtopics": _str_list(item.get("subtopics")),
        "activities": [],
        "est_hours": _hours(item.get("est_hours")),
        "topics": topics,
        "patterns": patterns,
    }


def validate_plan(
    data: dict, *, jd_text: str, topic_tracks: dict[str, str], pattern_slugs: set[str],
    hours_budget: int | None = None, company: str = "", sources: list[str] | None = None,
    topic_names: dict[str, str] | None = None,
) -> dict:
    """Turn a model reply into a clean plan dict, or raise PlanRejected.

    `topic_tracks` maps each linkable topic slug to its track (coding /
    aptitude / core-cs). With `hours_budget`, item hours are scaled so the plan
    fits the student's time (models estimate totals loosely; measured drift
    was up to ±40%). `sources` are the site names the research came from.
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

    # Sections: each kind once (a repeated kind is merged into the first), in track order.
    by_kind: dict[str, dict] = {}
    for section in data.get("sections") or []:
        if not isinstance(section, dict):
            continue
        kind = _choice(section.get("kind"), SECTION_KINDS, "")
        if not kind:
            continue
        target = by_kind.setdefault(kind, {"kind": kind, "title": PlanPhase.Kind(kind).label,
                                           "goal": _text(section.get("goal"), 400), "items": []})
        for item in section.get("items") or []:
            if isinstance(item, dict) and _text(item.get("title"), 200) and len(target["items"]) < MAX_ITEMS_PER_PHASE:
                target["items"].append(_clean_item(item, kind, topic_tracks, pattern_slugs, topic_names))
    phases = [by_kind[k] for k in SECTION_KINDS if k in by_kind and by_kind[k]["items"]]
    if not phases:
        raise PlanRejected("KAFKA couldn't build a plan from that description. Please try again with the full text.")
    if hours_budget:
        _fit_to_budget(phases, Decimal(hours_budget))

    return {
        "summary": _text(data.get("summary"), 1200),
        "requirements": requirements[:MAX_REQUIREMENTS],
        "research": validate_research(data.get("research"), company=company, sources=sources or [])
        if sources is not None else {},
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


_BASIS_LINE = re.compile(r"basis:\s*\**\s*(company|similar|none)", re.I)


def research_basis(text: str) -> str:
    """The 'Basis:' line of a research report: company | similar | none (none if missing)."""
    match = _BASIS_LINE.search(text or "")
    return match.group(1).lower() if match else "none"


def _search(provider, prompt: str):
    try:
        found = provider.research(system=prompts.RESEARCH_SYSTEM, prompt=prompt, max_tokens=settings.PREP_RESEARCH_MAX_TOKENS)
    except LLMError as exc:
        logger.warning("Interview research failed: %s", exc)
        return None
    logger.info("Interview research done (in=%s, out=%s tokens, sources=%s, basis=%s)",
                found.result.input_tokens, found.result.output_tokens, found.sources, research_basis(found.text))
    return found if found.text else None


def research_interviews(provider, *, role: str, company: str, jd_text: str = ""):
    """Web research into past interview experiences; None if the provider can't search or nothing useful turned up.

    First the company itself; if nothing is found for it, similar companies for
    the same role. Best effort by design: a plan built from the job description
    alone is better than no plan, so research problems are logged, not raised.
    """
    if not settings.PREP_RESEARCH or not getattr(provider, "supports_research", False):
        return None
    found = _search(provider, prompts.research_prompt(role=role, company=company))
    if company and (found is None or research_basis(found.text) == "none"):
        excerpt = jd_text[:500].strip()
        similar = _search(provider, prompts.similar_research_prompt(role=role, company=company, jd_excerpt=excerpt))
        if similar is not None and research_basis(similar.text) != "none":
            return similar
    if found is None or research_basis(found.text) == "none":
        return None
    return found


def generate_plan(
    user, *, role: str, job_description: str, company: str = "", candidate_info: str = "",
    days_available: int | None = None, hours_per_day: int | None = None,
) -> PreparationPlan:
    """Research, generate, validate and store a plan. Raises PlanRejected or LLMError."""
    provider = get_provider()
    if not provider.configured:
        raise LLMError("ASK KAFKA isn't configured yet (no API key on the server).", retryable=False)

    jd_text, truncated = clean_jd_text(job_description)
    topics, patterns = catalog_for_prompt()
    if days_available and not hours_per_day:
        hours_per_day = 2

    research = research_interviews(provider, role=role, company=company, jd_text=jd_text)
    prompt = prompts.user_prompt(
        role=role, company=company, candidate_info=candidate_info, days_available=days_available,
        hours_per_day=hours_per_day, jd_text=jd_text, topics=topics, patterns=patterns,
        research_text=research.text[:RESEARCH_CHARS] if research else None,
    )
    data, result = provider.complete_json(
        system=prompts.SYSTEM,
        prompt=prompt,
        schema=plan_schema(),
        name="study_plan",
        max_tokens=settings.PREP_PLAN_MAX_TOKENS,
        effort=settings.PREP_LLM_EFFORT,
        patient=research is not None,  # the research call may have used most of this minute's tokens
    )
    logger.info(
        "Study plan generated (model=%s, in=%s, out=%s tokens)", result.model, result.input_tokens, result.output_tokens
    )
    clean = validate_plan(
        data, jd_text=jd_text,
        topic_tracks={t["slug"]: t["track"] for t in topics}, pattern_slugs={p["slug"] for p in patterns},
        hours_budget=days_available * hours_per_day if days_available else None,
        company=company, sources=research.sources if research else None,
        topic_names={t["slug"]: t["name"] for t in topics},
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
        summary=clean["summary"], requirements=clean["requirements"], research=clean["research"],
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
                activities=item["activities"], est_hours=item["est_hours"], mode=item["mode"],
            )
            plan_item.topics.set([topic_ids[s] for s in item["topics"]])
            plan_item.patterns.set([pattern_ids[s] for s in item["patterns"]])
    return plan


# --- lessons -----------------------------------------------------------------------------


def validate_lesson(data: dict) -> dict:
    """Clean a generated lesson; raise LLMError (retryable) if it's unusable."""
    sections = []
    for sec in data.get("sections") or []:
        if isinstance(sec, dict) and _text(sec.get("body"), 1500):
            sections.append({"heading": _text(sec.get("heading"), 120), "body": _text(sec.get("body"), 1500)})
    quiz = []
    for q in data.get("quiz") or []:
        if not isinstance(q, dict):
            continue
        options = [_text(o, 200) for o in (q.get("options") or []) if _text(o, 200)]
        try:
            answer = int(q.get("answer"))
        except (TypeError, ValueError):
            continue
        if _text(q.get("question"), 400) and len(options) == 4 and 0 <= answer < 4 and len(set(options)) == 4:
            quiz.append({"question": _text(q.get("question"), 400), "options": options, "answer": answer,
                         "explanation": _text(q.get("explanation"), 400)})
    if len(sections) < 2 or len(quiz) < 3:
        raise LLMError("KAFKA couldn't write this lesson properly. Please try again.", retryable=True,
                       detail=f"sections={len(sections)} quiz={len(quiz)}")
    return {"sections": sections[:6], "key_points": _str_list(data.get("key_points"), 200)[:6], "quiz": quiz[:6]}


def generate_lesson(item: PlanItem) -> dict:
    """Notes + quiz for a lesson item: generated on first open, then stored and reused."""
    if item.lesson:
        return item.lesson
    provider = get_provider()
    if not provider.configured:
        raise LLMError("ASK KAFKA isn't configured yet (no API key on the server).", retryable=False)
    plan = item.phase.plan
    data, result = provider.complete_json(
        system=prompts.LESSON_SYSTEM,
        prompt=prompts.lesson_prompt(role=plan.role, company=plan.company, title=item.title,
                                     subtopics=item.subtopics, reason=item.reason),
        schema=lesson_schema(),
        name="lesson",
        max_tokens=settings.PREP_LESSON_MAX_TOKENS,
        effort=settings.PREP_LLM_EFFORT,
    )
    lesson = {**validate_lesson(data), "model": result.model}
    item.lesson = lesson
    item.save(update_fields=["lesson"])
    return lesson


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
