from rest_framework import serializers

from apps.catalog.serializers import ProgressStateSerializer, QuestionSummarySerializer, TopicSerializer

from .models import QuestionProgress


class AnswerInputSerializer(serializers.Serializer):
    option_id = serializers.IntegerField(min_value=1)


class ProgressUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[QuestionProgress.Status.COMPLETED])


class AnswerResultSerializer(serializers.Serializer):
    is_correct = serializers.BooleanField()
    correct_option_id = serializers.IntegerField()
    explanation = serializers.CharField()
    progress = ProgressStateSerializer()


class ActivityQuerySerializer(serializers.Serializer):
    days = serializers.ChoiceField(choices=[7, 14, 30, 90, 365], default=7)


class RecentQuerySerializer(serializers.Serializer):
    limit = serializers.IntegerField(min_value=1, max_value=50, default=10)


class RecentProgressSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()

    class Meta:
        model = QuestionProgress
        fields = ["question", "status", "is_correct", "updated_at", "completed_at"]

    def get_question(self, progress):
        question = progress.question
        question.user_status = progress.status  # summary serializer reads this
        return QuestionSummarySerializer(question).data


class PlanItemSerializer(serializers.Serializer):
    question = QuestionSummarySerializer()
    done = serializers.BooleanField()


class PlanSerializer(serializers.Serializer):
    date = serializers.DateField()
    daily_goal = serializers.IntegerField()
    completed_today = serializers.IntegerField()
    items = PlanItemSerializer(many=True)
    recommended_topics = TopicSerializer(many=True)
