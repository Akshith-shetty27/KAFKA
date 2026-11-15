"""Read-side queries for study plans. Always scoped to the requesting user."""

from django.db.models import Count, Prefetch, Q, Sum

from apps.catalog.selectors import topics_with_progress

from .models import PlanItem, PlanPhase, PreparationPlan


def my_plans(user):
    return PreparationPlan.objects.filter(user=user).annotate(
        item_count=Count("phases__items"),
        completed_count=Count("phases__items", filter=Q(phases__items__completed_at__isnull=False)),
        total_hours=Sum("phases__items__est_hours"),
    )


def plan_detail(user, pk) -> PreparationPlan | None:
    items = PlanItem.objects.prefetch_related("topics__category", "patterns").order_by("order")
    phases = PlanPhase.objects.prefetch_related(Prefetch("items", queryset=items)).order_by("order")
    plan = my_plans(user).prefetch_related(Prefetch("phases", queryset=phases)).filter(pk=pk).first()
    if plan is not None:
        # The student's progress on every topic a plan item links to (one query).
        plan.topic_progress = {t.slug: t for t in topics_with_progress(user)}
    return plan


def my_item(user, plan_pk, item_pk) -> PlanItem | None:
    return (
        PlanItem.objects.select_related("phase")
        .filter(pk=item_pk, phase__plan_id=plan_pk, phase__plan__user=user)
        .first()
    )
