"""
Two tables, two jobs:

* `QuestionProgress` — the *current state* of one user on one question
  ("have I finished this?"). One row per (user, question).
* `ActivityEvent` — an append-only *history* of what happened and when.
  Daily activity, streaks and answer accuracy are computed from it, so no
  counters are stored twice.
"""

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.catalog.models import Question, QuestionOption


class QuestionProgress(models.Model):
    class Status(models.TextChoices):
        ATTEMPTED = "attempted", "Attempted"
        COMPLETED = "completed", "Completed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="question_progress")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="progress_records")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ATTEMPTED)

    # MCQ only: how many times an answer was submitted, and how the last and
    # first submissions went.
    answer_count = models.PositiveIntegerField(default=0)
    is_correct = models.BooleanField(null=True, blank=True)
    first_attempt_correct = models.BooleanField(null=True, blank=True)
    selected_option = models.ForeignKey(
        QuestionOption, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    first_attempted_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "question progress"
        constraints = [
            models.UniqueConstraint(fields=["user", "question"], name="unique_progress_per_user_question"),
            models.CheckConstraint(condition=Q(status__in=["attempted", "completed"]), name="progress_valid_status"),
            models.CheckConstraint(
                condition=Q(status="attempted") | Q(completed_at__isnull=False),
                name="completed_progress_has_timestamp",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "-updated_at"]),
        ]

    def __str__(self):
        return f"{self.user} · {self.question} · {self.status}"


class ActivityEvent(models.Model):
    class Type(models.TextChoices):
        ATTEMPTED = "attempted", "Opened a question"
        ANSWERED = "answered", "Answered an MCQ"
        COMPLETED = "completed", "Completed a question"
        AI_MESSAGE = "ai_message", "Asked ASK KAFKA"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity_events")
    question = models.ForeignKey(
        Question, on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_events"
    )
    event_type = models.CharField(max_length=16, choices=Type.choices)
    is_correct = models.BooleanField(null=True, blank=True)  # set for ANSWERED events
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "created_at"])]

    def __str__(self):
        return f"{self.user} · {self.event_type} · {self.created_at:%Y-%m-%d %H:%M}"
