from rest_framework import serializers

from apps.catalog.serializers import CategoryRefSerializer

from .models import Conversation, Message, Mode


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "mode", "hint_level", "status", "created_at"]


class QuestionRefSerializer(serializers.Serializer):
    slug = serializers.CharField()
    title = serializers.CharField()
    question_type = serializers.CharField()
    category = serializers.SerializerMethodField()

    def get_category(self, question):
        return CategoryRefSerializer(question.topic.category).data


class ConversationSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "title", "question", "created_at", "updated_at", "last_message"]

    def get_question(self, conv):
        return QuestionRefSerializer(conv.question).data if conv.question else None

    def get_last_message(self, conv):
        last = getattr(conv, "_last_message", None)
        if last is None:
            return None
        return {"role": last.role, "preview": last.content[:140], "created_at": last.created_at}


class ConversationDetailSerializer(ConversationSerializer):
    """Context must provide `messages` and `capabilities`."""

    messages = serializers.SerializerMethodField()
    capabilities = serializers.SerializerMethodField()

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ["messages", "capabilities"]

    def get_messages(self, conv):
        return MessageSerializer(self.context["messages"], many=True).data

    def get_capabilities(self, conv):
        return self.context["capabilities"]


class ConversationCreateSerializer(serializers.Serializer):
    question_slug = serializers.SlugField(required=False, allow_blank=True)


class ConversationFilterSerializer(serializers.Serializer):
    question = serializers.SlugField(required=False)


class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=4000, trim_whitespace=True)
    mode = serializers.ChoiceField(choices=Mode.values, default=Mode.CHAT)
    hint_level = serializers.IntegerField(min_value=1, max_value=3, required=False, allow_null=True)

    def validate(self, attrs):
        if attrs["mode"] == Mode.HINT and not attrs.get("hint_level"):
            attrs["hint_level"] = 1
        return attrs
