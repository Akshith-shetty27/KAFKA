from rest_framework import serializers

from .models import PlanItem, PlanPhase, PreparationPlan


class PlanCreateSerializer(serializers.Serializer):
    role = serializers.CharField(max_length=120)
    company = serializers.CharField(max_length=120, required=False, allow_blank=True, default="")
    job_description = serializers.CharField(trim_whitespace=True)
    candidate_info = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")
    days_available = serializers.IntegerField(min_value=1, max_value=180, required=False, allow_null=True, default=None)
    hours_per_day = serializers.IntegerField(min_value=1, max_value=12, required=False, allow_null=True, default=None)


class ItemCompletionSerializer(serializers.Serializer):
    completed = serializers.BooleanField()


def _progress(plan) -> dict:
    return {
        "completed_items": plan.completed_count or 0,
        "total_items": plan.item_count or 0,
        "total_hours": float(plan.total_hours or 0),
    }


class PlanListSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()

    class Meta:
        model = PreparationPlan
        fields = ["id", "role", "company", "days_available", "created_at", "updated_at", "progress"]

    def get_progress(self, plan):
        return _progress(plan)


def mock_prompt(item, plan) -> str:
    """The opening message for an Ask KAFKA mock interview of this round."""
    where = f" at {plan.company}" if plan.company else ""
    focus = f" Focus on: {', '.join(item.subtopics)}." if item.subtopics else ""
    return (
        f"Run a mock interview for the \"{item.title}\" round, for a {plan.role} role{where}.{focus} "
        "Ask me one question at a time, wait for my answer, then give short feedback and a better answer "
        "before the next question. Start with the first question."
    )


class PlanItemSerializer(serializers.ModelSerializer):
    category_label = serializers.CharField(source="get_category_display")
    mode_label = serializers.CharField(source="get_mode_display")
    completed = serializers.BooleanField()
    est_hours = serializers.FloatField()
    topics = serializers.SerializerMethodField()
    patterns = serializers.SerializerMethodField()
    mock_prompt = serializers.SerializerMethodField()

    class Meta:
        model = PlanItem
        fields = [
            "id", "title", "mode", "mode_label", "category", "category_label", "importance", "reason", "subtopics",
            "activities", "est_hours", "completed", "completed_at", "topics", "patterns", "lesson", "mock_prompt",
        ]

    def get_mock_prompt(self, item):
        plan = self.context.get("plan")
        return mock_prompt(item, plan) if plan is not None and item.mode == PlanItem.Mode.MOCK else None

    def get_topics(self, item):
        progress = self.context.get("topic_progress", {})
        out = []
        for t in item.topics.all():
            p = progress.get(t.slug)
            out.append(
                {
                    "slug": t.slug,
                    "name": t.name,
                    "category": t.category.slug,
                    "question_count": getattr(p, "question_count", 0),
                    "completed_count": getattr(p, "completed_count", 0),
                }
            )
        return out

    def get_patterns(self, item):
        return [{"slug": p.slug, "name": p.name} for p in item.patterns.all()]


class PlanPhaseSerializer(serializers.ModelSerializer):
    kind_label = serializers.CharField(source="get_kind_display")
    est_hours = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    class Meta:
        model = PlanPhase
        fields = ["id", "order", "kind", "kind_label", "title", "goal", "est_hours", "items"]

    def get_est_hours(self, phase):
        return float(sum(i.est_hours for i in phase.items.all()))

    def get_items(self, phase):
        return PlanItemSerializer(phase.items.all(), many=True, context=self.context).data


class PlanDetailSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()
    phases = serializers.SerializerMethodField()

    class Meta:
        model = PreparationPlan
        fields = [
            "id", "role", "company", "job_description", "jd_truncated", "candidate_info", "days_available",
            "hours_per_day", "summary", "requirements", "research", "model", "created_at", "updated_at", "progress",
            "phases",
        ]

    def get_progress(self, plan):
        return _progress(plan)

    def get_phases(self, plan):
        context = {"topic_progress": getattr(plan, "topic_progress", {}), "plan": plan}
        return PlanPhaseSerializer(plan.phases.all(), many=True, context=context).data
