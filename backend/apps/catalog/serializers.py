from rest_framework import serializers

from apps.progress.models import QuestionProgress

from .models import Category, CodingDetail, Difficulty, Pattern, Question, QuestionType, Solution, Topic


# --- small reference shapes reused across responses -------------------------


class CategoryRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["slug", "name"]


class TopicRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["slug", "name"]


class PatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pattern
        fields = ["slug", "name", "description"]


class ProgressCountsMixin(serializers.Serializer):
    question_count = serializers.IntegerField(read_only=True)
    attempted_count = serializers.IntegerField(read_only=True)
    completed_count = serializers.IntegerField(read_only=True)


# --- lists -------------------------------------------------------------------


class CategorySerializer(ProgressCountsMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["slug", "name", "description", "glyph", "question_count", "attempted_count", "completed_count"]


class TopicSerializer(ProgressCountsMixin, serializers.ModelSerializer):
    category = CategoryRefSerializer(read_only=True)
    section = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            "slug",
            "name",
            "description",
            "category",
            "section",
            "question_count",
            "attempted_count",
            "completed_count",
        ]

    def get_section(self, topic):
        return {"slug": topic.section.slug, "name": topic.section.name} if topic.section else None


class QuestionSummarySerializer(serializers.ModelSerializer):
    """One row in a question list. `status` is this user's status or null."""

    topic = TopicRefSerializer(read_only=True)
    category = serializers.SerializerMethodField()
    patterns = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["slug", "title", "question_type", "difficulty", "topic", "category", "patterns", "status"]

    def get_category(self, question):
        return CategoryRefSerializer(question.topic.category).data

    def get_patterns(self, question):
        return [{"slug": p.slug, "name": p.name} for p in question.patterns.all()]

    def get_status(self, question):
        return getattr(question, "user_status", None)


class QuestionFilterSerializer(serializers.Serializer):
    """Validates the query string of GET /questions/."""

    STATUS_CHOICES = ["not_started", QuestionProgress.Status.ATTEMPTED, QuestionProgress.Status.COMPLETED]

    category = serializers.SlugField(required=False)
    topic = serializers.SlugField(required=False)
    difficulty = serializers.ChoiceField(choices=Difficulty.values, required=False)
    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False)
    pattern = serializers.SlugField(required=False)
    search = serializers.CharField(required=False, max_length=100, trim_whitespace=True)


# --- detail ------------------------------------------------------------------


class CodingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingDetail
        fields = ["constraints", "examples", "approach", "time_complexity", "space_complexity"]


class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = ["language", "code", "notes"]


class ProgressStateSerializer(serializers.ModelSerializer):
    selected_option_id = serializers.IntegerField(allow_null=True, read_only=True)

    class Meta:
        model = QuestionProgress
        fields = [
            "status",
            "answer_count",
            "is_correct",
            "first_attempt_correct",
            "selected_option_id",
            "first_attempted_at",
            "completed_at",
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
    """
    Full question. Context must provide `progress` (the user's
    QuestionProgress or None) and `navigation` ({previous, next, position, total}).

    For MCQs the correct option and the explanation are withheld until this
    user has answered at least once — the browser never receives the answer
    early, so it can't be read from the network tab.
    """

    topic = TopicRefSerializer(read_only=True)
    category = serializers.SerializerMethodField()
    patterns = serializers.SerializerMethodField()
    coding = serializers.SerializerMethodField()
    solutions = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()
    explanation = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    navigation = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "slug",
            "title",
            "question_type",
            "difficulty",
            "statement",
            "topic",
            "category",
            "patterns",
            "coding",
            "solutions",
            "options",
            "explanation",
            "answer",
            "progress",
            "navigation",
        ]

    # helpers
    def _progress(self):
        return self.context.get("progress")

    def _answer_revealed(self, question):
        if question.question_type != QuestionType.MCQ:
            return True
        progress = self._progress()
        return bool(progress and progress.answer_count > 0)

    # fields
    def get_category(self, question):
        return CategoryRefSerializer(question.topic.category).data

    def get_patterns(self, question):
        return [{"slug": p.slug, "name": p.name} for p in question.patterns.all()]

    def get_coding(self, question):
        if question.question_type != QuestionType.CODING or not hasattr(question, "coding"):
            return None
        return CodingDetailSerializer(question.coding).data

    def get_solutions(self, question):
        preferred = self.context.get("preferred_language")
        solutions = sorted(question.solutions.all(), key=lambda s: (s.language != preferred, s.language))
        return SolutionSerializer(solutions, many=True).data

    def get_options(self, question):
        if question.question_type != QuestionType.MCQ:
            return []
        return [{"id": o.id, "label": o.label, "text": o.text} for o in question.options.all()]

    def get_explanation(self, question):
        return question.explanation if self._answer_revealed(question) else None

    def get_answer(self, question):
        if question.question_type != QuestionType.MCQ or not self._answer_revealed(question):
            return None
        correct = next((o for o in question.options.all() if o.is_correct), None)
        return {"correct_option_id": correct.id if correct else None}

    def get_progress(self, question):
        progress = self._progress()
        return ProgressStateSerializer(progress).data if progress else None

    def get_navigation(self, question):
        return self.context.get("navigation")
