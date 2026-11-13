"""
Read-side queries for the catalog. Every function that returns progress
information takes `user` and only ever looks at that user's rows.
"""

from django.db.models import Count, OuterRef, Prefetch, Q, Subquery

from apps.progress.models import QuestionProgress

from .models import Category, Question, QuestionOption, Topic

COMPLETED = QuestionProgress.Status.COMPLETED


def _attach_progress(objects, user, group_field: str):
    """Set `attempted_count` / `completed_count` on each object from the user's rows.

    Counting through a join over *all* users' progress would get slower as
    the user base grows; grouping only this user's rows uses the
    (user, status) index and stays fast.
    """
    rows = (
        QuestionProgress.objects.filter(user=user, question__is_published=True)
        .values(group_field)
        .annotate(attempted=Count("id"), completed=Count("id", filter=Q(status=COMPLETED)))
    )
    by_key = {row[group_field]: row for row in rows}
    for obj in objects:
        row = by_key.get(obj.pk, {})
        obj.attempted_count = row.get("attempted", 0)
        obj.completed_count = row.get("completed", 0)
    return objects


def categories_with_progress(user) -> list[Category]:
    categories = Category.objects.annotate(
        question_count=Count("topics__questions", filter=Q(topics__questions__is_published=True))
    ).order_by("order", "name")
    return _attach_progress(list(categories), user, "question__topic__category_id")


def topics_with_progress(user, *, category: str | None = None) -> list[Topic]:
    qs = Topic.objects.select_related("category", "section").annotate(
        question_count=Count("questions", filter=Q(questions__is_published=True))
    )
    if category:
        qs = qs.filter(category__slug=category)
    qs = qs.order_by("category__order", "section__order", "order", "name")
    return _attach_progress(list(qs), user, "question__topic_id")


def published_questions():
    return Question.objects.filter(is_published=True)


def _with_user_status(qs, user):
    status = QuestionProgress.objects.filter(user=user, question=OuterRef("pk")).values("status")[:1]
    return qs.annotate(user_status=Subquery(status))


def question_list(user, *, category=None, topic=None, difficulty=None, status=None, pattern=None, search=None):
    qs = _with_user_status(published_questions(), user).select_related("topic__category")
    qs = qs.prefetch_related("patterns")
    if category:
        qs = qs.filter(topic__category__slug=category)
    if topic:
        qs = qs.filter(topic__slug=topic)
    if difficulty:
        qs = qs.filter(difficulty=difficulty)
    if pattern:
        # A question has each pattern at most once, so this join can't duplicate rows.
        qs = qs.filter(patterns__slug=pattern)
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(topic__name__icontains=search))
    if status == "not_started":
        qs = qs.filter(user_status__isnull=True)
    elif status:
        qs = qs.filter(user_status=status)
    return qs.order_by("topic__category__order", "topic__order", "order", "id")


def question_detail(slug: str):
    """Published question with everything the detail page needs, or None."""
    return (
        published_questions()
        .select_related("topic__category", "coding")
        .prefetch_related("patterns", "solutions", Prefetch("options", queryset=QuestionOption.objects.order_by("label")))
        .filter(slug=slug)
        .first()
    )


def question_navigation(question) -> dict:
    """Previous / next published question in the same topic (by curriculum order)."""
    slugs = list(
        published_questions().filter(topic_id=question.topic_id).order_by("order", "id").values_list("slug", flat=True)
    )
    index = slugs.index(question.slug)
    return {
        "previous": slugs[index - 1] if index > 0 else None,
        "next": slugs[index + 1] if index < len(slugs) - 1 else None,
    }
