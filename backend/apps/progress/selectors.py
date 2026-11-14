"""
Read-side statistics. Everything here is computed from QuestionProgress
(current state) and ActivityEvent (history) for one user — nothing is cached
or stored twice.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.catalog import selectors as catalog_selectors
from apps.catalog.models import Category

from .models import ActivityEvent, QuestionProgress

Status = QuestionProgress.Status
Event = ActivityEvent.Type
QUESTION_EVENTS = [Event.ATTEMPTED, Event.ANSWERED, Event.COMPLETED]


def local_today(user) -> date:
    return timezone.now().astimezone(user.profile.tzinfo).date()


# --- streaks -----------------------------------------------------------------


@dataclass(frozen=True)
class Streak:
    current: int
    longest: int
    active_today: bool


def compute_streaks(active_days: Iterable[date], today: date) -> Streak:
    """Pure function, unit-tested separately.

    The current streak is still alive if the user was active yesterday but
    hasn't done anything yet today — it only breaks after a full missed day.
    """
    days = set(active_days)
    active_today = today in days

    current = 0
    cursor = today if active_today else today - timedelta(days=1)
    while cursor in days:
        current += 1
        cursor -= timedelta(days=1)

    longest = run = 0
    previous = None
    for day in sorted(days):
        run = run + 1 if previous is not None and day - previous == timedelta(days=1) else 1
        longest = max(longest, run)
        previous = day

    return Streak(current=current, longest=longest, active_today=active_today)


def active_days(user) -> list[date]:
    tz = user.profile.tzinfo
    return list(
        ActivityEvent.objects.filter(user=user)
        .annotate(day=TruncDate("created_at", tzinfo=tz))
        .values_list("day", flat=True)
        .distinct()
    )


def streak(user) -> Streak:
    return compute_streaks(active_days(user), local_today(user))


# --- dashboard summary ---------------------------------------------------------


def summary(user) -> dict:
    total_questions = catalog_selectors.published_questions().count()
    progress = QuestionProgress.objects.filter(user=user, question__is_published=True).aggregate(
        attempted=Count("id"), completed=Count("id", filter=Q(status=Status.COMPLETED))
    )

    answers = ActivityEvent.objects.filter(user=user, event_type=Event.ANSWERED)
    answer_totals = answers.aggregate(total=Count("id"), correct=Count("id", filter=Q(is_correct=True)))
    answers_by_category = {
        row["question__topic__category_id"]: row
        for row in answers.values("question__topic__category_id").annotate(
            total=Count("id"), correct=Count("id", filter=Q(is_correct=True))
        )
    }

    categories = []
    for category in catalog_selectors.categories_with_progress(user):
        cat_answers = answers_by_category.get(category.pk, {})
        categories.append(
            {
                "slug": category.slug,
                "name": category.name,
                "glyph": category.glyph,
                "question_count": category.question_count,
                "attempted_count": category.attempted_count,
                "completed_count": category.completed_count,
                "answers_total": cat_answers.get("total", 0),
                "answers_correct": cat_answers.get("correct", 0),
            }
        )

    s = streak(user)
    answered = answer_totals["total"]
    return {
        "totals": {
            "questions": total_questions,
            "attempted": progress["attempted"],
            "completed": progress["completed"],
            "completion_rate": round(progress["completed"] / total_questions, 4) if total_questions else 0.0,
        },
        "answers": {
            "total": answered,
            "correct": answer_totals["correct"],
            "incorrect": answered - answer_totals["correct"],
            "accuracy": round(answer_totals["correct"] / answered, 4) if answered else None,
        },
        "streak": {"current": s.current, "longest": s.longest, "active_today": s.active_today},
        "categories": categories,
    }


# --- daily activity --------------------------------------------------------------


def daily_activity(user, days: int) -> list[dict]:
    """One entry per local day for the last `days` days (oldest first), zero-filled."""
    tz = user.profile.tzinfo
    today = local_today(user)
    start = today - timedelta(days=days - 1)
    start_at = datetime.combine(start, time.min, tzinfo=tz)

    rows = (
        ActivityEvent.objects.filter(user=user, created_at__gte=start_at)
        .annotate(day=TruncDate("created_at", tzinfo=tz))
        .values("day")
        .annotate(
            questions=Count("question", filter=Q(event_type__in=QUESTION_EVENTS), distinct=True),
            completed=Count("id", filter=Q(event_type=Event.COMPLETED)),
            answered=Count("id", filter=Q(event_type=Event.ANSWERED)),
            ai_messages=Count("id", filter=Q(event_type=Event.AI_MESSAGE)),
        )
    )
    by_day = {row["day"]: row for row in rows}

    series = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        row = by_day.get(day, {})
        series.append(
            {
                "date": day.isoformat(),
                "questions": row.get("questions", 0),
                "completed": row.get("completed", 0),
                "answered": row.get("answered", 0),
                "ai_messages": row.get("ai_messages", 0),
            }
        )
    return series


# --- recent ------------------------------------------------------------------------


def recent_progress(user, limit: int = 10):
    return (
        QuestionProgress.objects.filter(user=user, question__is_published=True)
        .select_related("question__topic__category")
        .prefetch_related("question__patterns")
        .order_by("-updated_at")[:limit]
    )


# --- today's plan & recommendations -------------------------------------------------


def recommended_topics(user) -> list:
    """One topic per category to focus on next.

    Topics the student has started but not finished come first (finish what
    you started), then the least-complete topic, then curriculum order.
    """
    best = {}
    for topic in catalog_selectors.topics_with_progress(user):
        if topic.question_count == 0 or topic.completed_count >= topic.question_count:
            continue
        started = topic.attempted_count > 0
        key = (0 if started else 1, topic.completed_count / topic.question_count)
        current = best.get(topic.category_id)
        if current is None or key < current[0]:
            best[topic.category_id] = (key, topic)
    ordered = sorted(best.values(), key=lambda item: (item[1].category.order, item[1].category.name))
    return [topic for _, topic in ordered]


def _split_goal(goal: int, category_count: int) -> list[int]:
    """Spread the daily goal across categories round-robin: 5 → [2, 2, 1]."""
    quotas = [0] * category_count
    for i in range(goal):
        quotas[i % category_count] += 1
    return quotas


def todays_plan(user) -> dict:
    """
    A deterministic plan for today: `daily_goal` questions spread across
    categories. Questions completed today fill their category's slots first
    (shown as done); the rest are the next unfinished questions, starting
    with the recommended topic for that category.
    """
    goal = user.profile.daily_goal
    day_start = datetime.combine(local_today(user), time.min, tzinfo=user.profile.tzinfo)
    topics = recommended_topics(user)
    recommended_by_category = {t.category_id: t for t in topics}

    categories = [c for c in Category.objects.order_by("order", "name") if c.topics.exists()]
    quotas = _split_goal(goal, len(categories)) if categories else []

    completed_today_ids = list(
        ActivityEvent.objects.filter(user=user, event_type=Event.COMPLETED, created_at__gte=day_start)
        .order_by("created_at")
        .values_list("question_id", flat=True)
    )
    completed_ids = set(
        QuestionProgress.objects.filter(user=user, status=Status.COMPLETED).values_list("question_id", flat=True)
    )

    items = []
    for category, quota in zip(categories, quotas):
        if quota == 0:
            continue
        base = catalog_selectors.question_list(user, category=category.slug)

        done_ids = [qid for qid in dict.fromkeys(completed_today_ids) if qid in completed_ids]
        done = list(base.filter(id__in=done_ids)[:quota])
        for question in done:
            items.append({"question": question, "done": True})

        remaining = quota - len(done)
        if remaining > 0:
            recommended = recommended_by_category.get(category.pk)
            todo = base.exclude(id__in=completed_ids)
            if recommended:
                todo = todo.annotate(
                    priority=Case(When(topic_id=recommended.pk, then=Value(0)), default=Value(1), output_field=IntegerField())
                ).order_by("priority", "topic__order", "order", "id")
            for question in todo[:remaining]:
                items.append({"question": question, "done": False})

    return {
        "date": local_today(user).isoformat(),
        "daily_goal": goal,
        "completed_today": sum(1 for item in items if item["done"]),
        "items": items,
        "recommended_topics": topics,
    }


# --- insights (Progress page) ---------------------------------------------------------

DIFFICULTY_ORDER = ["easy", "medium", "hard"]
FOCUS_ACCURACY_BELOW = 0.7  # first-try MCQ accuracy that flags a topic
FOCUS_MIN_ANSWERS = 2  # don't judge a topic on a single answer
FOCUS_LIMIT = 3


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def focus_areas(topics: list[dict]) -> list[dict]:
    """Up to three topics worth attention, most urgent first.

    1. MCQ topics where first-try accuracy is low (≥2 first tries, < 70%).
    2. Topics started but less than half done.
    Pure function over `insights()` topic rows — unit-tested separately.
    """
    weak = sorted(
        (
            t
            for t in topics
            if t["first_attempt_total"] >= FOCUS_MIN_ANSWERS
            and t["first_attempt_correct"] / t["first_attempt_total"] < FOCUS_ACCURACY_BELOW
        ),
        key=lambda t: (t["first_attempt_correct"] / t["first_attempt_total"], -t["first_attempt_total"]),
    )
    unfinished = sorted(
        (
            t
            for t in topics
            if t["attempted_count"] > 0 and t["question_count"] and t["completed_count"] / t["question_count"] < 0.5
        ),
        key=lambda t: t["completed_count"] / t["question_count"],
    )
    result, seen = [], set()
    for reason, group in (("low_accuracy", weak), ("unfinished", unfinished)):
        for t in group:
            if t["slug"] not in seen and len(result) < FOCUS_LIMIT:
                seen.add(t["slug"])
                result.append({"reason": reason, "topic": t})
    return result


def insights(user) -> dict:
    """Breakdowns for the Progress page: per topic, per difficulty, focus areas."""
    published = catalog_selectors.published_questions()

    totals_by_difficulty = dict(published.values_list("difficulty").annotate(n=Count("id")))
    done_by_difficulty = dict(
        QuestionProgress.objects.filter(user=user, status=Status.COMPLETED, question__is_published=True)
        .values_list("question__difficulty")
        .annotate(n=Count("id"))
    )
    difficulty = [
        {"difficulty": d, "question_count": totals_by_difficulty.get(d, 0), "completed_count": done_by_difficulty.get(d, 0)}
        for d in DIFFICULTY_ORDER
    ]

    answers = {
        row["question__topic_id"]: row
        for row in ActivityEvent.objects.filter(user=user, event_type=Event.ANSWERED)
        .values("question__topic_id")
        .annotate(total=Count("id"), correct=Count("id", filter=Q(is_correct=True)))
    }
    first_tries = {
        row["question__topic_id"]: row
        for row in QuestionProgress.objects.filter(user=user, answer_count__gt=0, question__is_published=True)
        .values("question__topic_id")
        .annotate(total=Count("id"), correct=Count("id", filter=Q(first_attempt_correct=True)))
    }

    topics = []
    for topic in catalog_selectors.topics_with_progress(user):
        a = answers.get(topic.pk, {})
        f = first_tries.get(topic.pk, {})
        topics.append(
            {
                "slug": topic.slug,
                "name": topic.name,
                "category": {"slug": topic.category.slug, "name": topic.category.name},
                "section": topic.section.name if topic.section else None,
                "question_count": topic.question_count,
                "attempted_count": topic.attempted_count,
                "completed_count": topic.completed_count,
                "answers_total": a.get("total", 0),
                "answers_correct": a.get("correct", 0),
                "first_attempt_total": f.get("total", 0),
                "first_attempt_correct": f.get("correct", 0),
                "first_attempt_accuracy": _ratio(f.get("correct", 0), f.get("total", 0)),
            }
        )

    return {"difficulty": difficulty, "topics": topics, "focus_areas": focus_areas(topics)}
