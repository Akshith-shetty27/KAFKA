"""
Write-side progress logic. Every function takes the acting `user`
explicitly, so a request can only ever change its own records.
"""

from dataclasses import dataclass
from datetime import datetime, time

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.catalog.models import Question, QuestionOption, QuestionType

from .models import ActivityEvent, QuestionProgress

Status = QuestionProgress.Status
Event = ActivityEvent.Type


def log_event(user, event_type, *, question=None, is_correct=None) -> ActivityEvent:
    return ActivityEvent.objects.create(user=user, event_type=event_type, question=question, is_correct=is_correct)


def local_day_start(user) -> datetime:
    """Midnight today in the user's timezone (as an aware datetime)."""
    tz = user.profile.tzinfo
    today = timezone.now().astimezone(tz).date()
    return datetime.combine(today, time.min, tzinfo=tz)


def record_attempt(user, question: Question) -> QuestionProgress:
    """The user opened / started a question.

    Creates the progress row on first visit. An `attempted` event is logged at
    most once per question per (local) day, so refreshing a page doesn't
    inflate daily activity.
    """
    now = timezone.now()
    progress, created = QuestionProgress.objects.get_or_create(
        user=user, question=question, defaults={"status": Status.ATTEMPTED, "first_attempted_at": now}
    )
    if not created:
        # Bump updated_at so "recently attempted" reflects the latest visit.
        QuestionProgress.objects.filter(pk=progress.pk).update(updated_at=now)
        progress.updated_at = now

    already_logged_today = ActivityEvent.objects.filter(
        user=user, question=question, event_type=Event.ATTEMPTED, created_at__gte=local_day_start(user)
    ).exists()
    if not already_logged_today:
        log_event(user, Event.ATTEMPTED, question=question)
    return progress


@dataclass(frozen=True)
class AnswerResult:
    is_correct: bool
    correct_option_id: int
    explanation: str
    progress: QuestionProgress


def submit_answer(user, question: Question, option_id: int) -> AnswerResult:
    """Grade an MCQ answer on the server.

    Status becomes `completed` the first time the user answers correctly.
    `first_attempt_correct` is fixed by the very first submission, so
    retrying can't rewrite the user's real accuracy.
    """
    if question.question_type != QuestionType.MCQ:
        raise ValidationError({"option_id": ["This question is not multiple choice."]})
    try:
        option = question.options.get(pk=option_id)
    except QuestionOption.DoesNotExist:
        raise ValidationError({"option_id": ["That option does not belong to this question."]})

    now = timezone.now()
    with transaction.atomic():
        # Lock the row so two quick submissions can't both count as "first".
        progress, _ = QuestionProgress.objects.select_for_update().get_or_create(
            user=user, question=question, defaults={"status": Status.ATTEMPTED, "first_attempted_at": now}
        )
        if progress.answer_count == 0:
            progress.first_attempt_correct = option.is_correct
        progress.answer_count += 1
        progress.is_correct = option.is_correct
        progress.selected_option = option
        newly_completed = option.is_correct and progress.status != Status.COMPLETED
        if newly_completed:
            progress.status = Status.COMPLETED
            progress.completed_at = now
        progress.save()

        log_event(user, Event.ANSWERED, question=question, is_correct=option.is_correct)
        if newly_completed:
            log_event(user, Event.COMPLETED, question=question)

    correct = question.options.get(is_correct=True)
    return AnswerResult(
        is_correct=option.is_correct,
        correct_option_id=correct.pk,
        explanation=question.explanation,
        progress=progress,
    )


def mark_completed(user, question: Question) -> QuestionProgress:
    """Coding and concept questions are completed by the student's own judgement."""
    if question.question_type == QuestionType.MCQ:
        raise ValidationError({"status": ["Multiple-choice questions are completed by answering them correctly."]})

    now = timezone.now()
    with transaction.atomic():
        progress, _ = QuestionProgress.objects.select_for_update().get_or_create(
            user=user, question=question, defaults={"first_attempted_at": now}
        )
        if progress.status != Status.COMPLETED:
            progress.status = Status.COMPLETED
            progress.completed_at = now
            progress.save()
            log_event(user, Event.COMPLETED, question=question)
    return progress


def reset_progress(user, question: Question) -> None:
    """Forget the user's state on a question. History (events) is kept."""
    QuestionProgress.objects.filter(user=user, question=question).delete()
