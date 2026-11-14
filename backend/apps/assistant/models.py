"""
ASK KAFKA conversation history.

A Conversation may be tied to a question (opened from a question page) or be
a general chat. Messages are stored in full; only the recent ones are sent to
the model (see services.build_history).
"""

from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.catalog.models import Question
from apps.core.models import TimeStampedModel


class Mode(models.TextChoices):
    CHAT = "chat", "Chat"
    HINT = "hint", "Hint"
    EXPLAIN = "explain", "Explain the solution"
    REVIEW = "review", "Review my answer"


class Conversation(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations")
    question = models.ForeignKey(
        Question, on_delete=models.SET_NULL, null=True, blank=True, related_name="conversations"
    )
    title = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["user", "-updated_at"])]

    def __str__(self):
        return self.title or f"Conversation {self.pk}"


class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user", "Student"
        ASSISTANT = "assistant", "ASK KAFKA"

    class Status(models.TextChoices):
        COMPLETE = "complete", "Complete"
        INCOMPLETE = "incomplete", "Incomplete"  # stream stopped early or hit the token limit
        ERROR = "error", "Error"
        REFUSED = "refused", "Declined"

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField(blank=True)
    # What the student asked for (user messages only).
    mode = models.CharField(max_length=10, choices=Mode.choices, default=Mode.CHAT)
    hint_level = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.COMPLETE)
    # Bookkeeping for assistant messages (cost tracking, debugging).
    provider = models.CharField(max_length=32, blank=True)
    model = models.CharField(max_length=64, blank=True)
    input_tokens = models.PositiveIntegerField(null=True, blank=True)
    output_tokens = models.PositiveIntegerField(null=True, blank=True)
    cache_read_tokens = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [models.Index(fields=["conversation", "created_at"])]
        constraints = [
            models.CheckConstraint(
                condition=Q(hint_level__isnull=True) | Q(hint_level__gte=1, hint_level__lte=3),
                name="message_hint_level_1_to_3",
            ),
        ]

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"
