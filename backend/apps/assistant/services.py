"""
ASK KAFKA business logic: conversations, history, and streaming one turn.

`stream_turn` is a generator of plain dict events consumed by the SSE view:

    {"type": "start", "user_message": {...}, "conversation": {"id", "title"}}
    {"type": "token", "text": "..."}            (many)
    {"type": "done",  "message": {...}}         assistant message saved
    {"type": "error", "message": "...", "retryable": bool, "saved": {...} | None}

Whatever happens — success, provider error, the student closing the tab —
the assistant's (possibly partial) reply is saved, so history never has a
silent gap.
"""

import logging
from collections.abc import Iterator

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.progress.models import ActivityEvent
from apps.progress.services import log_event

from . import context, prompts
from .llm import ChatTurn, Finished, LLMError, TextDelta, get_provider, max_reply_tokens
from .models import Conversation, Message, Mode

logger = logging.getLogger(__name__)

TITLE_LENGTH = 60
STOP_NOTES = {
    "max_tokens": "\n\n_(Reply cut short — ask KAFKA to continue.)_",
    "refusal": "\n\n_ASK KAFKA can't help with that request. Try rephrasing it around your interview preparation._",
}


def create_conversation(user, *, question=None, title: str = "") -> Conversation:
    """A new conversation, titled by its question, by `title`, or (later) by its first message."""
    return Conversation.objects.create(user=user, question=question, title=question.title if question else title.strip())


def build_history(conversation: Conversation, limit: int, max_chars: int | None = None) -> list[ChatTurn]:
    """The most recent usable messages as alternating user/assistant turns.

    At most `limit` messages and (if given) about `max_chars` characters —
    the newest message is always kept. The character budget keeps requests
    inside per-minute token limits (≈4 characters per token). Failed or
    empty replies are skipped; consecutive messages from the same role are
    merged, and the history always starts with the student.
    """
    newest_first = list(
        conversation.messages.exclude(status=Message.Status.ERROR)
        .exclude(content="")
        .order_by("-created_at", "-id")[:limit]
    )
    rows, used = [], 0
    for msg in newest_first:
        if rows and max_chars is not None and used + len(msg.content) > max_chars:
            break
        rows.append(msg)
        used += len(msg.content)
    rows.reverse()
    turns: list[ChatTurn] = []
    for msg in rows:
        if turns and turns[-1].role == msg.role:
            turns[-1] = ChatTurn(msg.role, f"{turns[-1].content}\n\n{msg.content}")
        else:
            turns.append(ChatTurn(msg.role, msg.content))
    while turns and turns[0].role != "user":
        turns.pop(0)
    return turns


def _serialize(msg: Message) -> dict:
    from .serializers import MessageSerializer

    return MessageSerializer(msg).data


def stream_turn(user, conversation: Conversation, *, content: str, mode: str, hint_level: int | None = None) -> Iterator[dict]:
    """Validate now (so the view can answer 400), then return the event generator.

    A generator body only runs once iteration starts — after the HTTP 200 has
    been sent — so validation must happen before it.
    """
    context.check_mode_allowed(user, conversation.question, mode)
    return _run_turn(user, conversation, content=content, mode=mode, hint_level=hint_level)


def _run_turn(user, conversation: Conversation, *, content: str, mode: str, hint_level: int | None) -> Iterator[dict]:
    question = conversation.question
    with transaction.atomic():
        user_msg = Message.objects.create(
            conversation=conversation,
            role=Message.Role.USER,
            content=content,
            mode=mode,
            hint_level=hint_level if mode == Mode.HINT else None,
        )
        if not conversation.title:
            conversation.title = content[:TITLE_LENGTH].strip() + ("…" if len(content) > TITLE_LENGTH else "")
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=["title", "updated_at"])
    log_event(user, ActivityEvent.Type.AI_MESSAGE, question=question)
    yield {
        "type": "start",
        "user_message": _serialize(user_msg),
        "conversation": {"id": conversation.pk, "title": conversation.title},
    }

    question_context = context.build_question_context(user, question, mode)[0] if question else None
    system = prompts.build_system_prompt(
        mode=mode,
        hint_level=hint_level,
        question_context=question_context,
        preferred_language=user.profile.get_preferred_language_display(),
    )
    history = build_history(conversation, settings.LLM_HISTORY_MESSAGES, settings.LLM_HISTORY_CHARS)
    provider = get_provider()

    parts: list[str] = []
    result = None

    def save(status: str, extra: str = "") -> Message:
        return Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content="".join(parts) + extra,
            status=status,
            provider=provider.name,
            model=(result.model if result else provider.model),
            input_tokens=result.input_tokens if result else None,
            output_tokens=result.output_tokens if result else None,
            cache_read_tokens=result.cache_read_tokens if result else None,
        )

    try:
        for event in provider.stream(system=system, messages=history, max_tokens=max_reply_tokens()):
            if isinstance(event, TextDelta):
                parts.append(event.text)
                yield {"type": "token", "text": event.text}
            elif isinstance(event, Finished):
                result = event.result
    except LLMError as exc:
        logger.warning("ASK KAFKA provider error (conversation %s): %s", conversation.pk, exc)
        saved = save(Message.Status.ERROR) if parts else None
        yield {
            "type": "error",
            "message": exc.user_message,
            "retryable": exc.retryable,
            "saved": _serialize(saved) if saved else None,
        }
        return
    except GeneratorExit:
        # The student closed the page / pressed stop: keep what we have.
        if parts:
            save(Message.Status.INCOMPLETE)
        raise

    stop = result.stop_reason if result else "end_turn"
    note = STOP_NOTES.get(stop, "")
    if note:
        yield {"type": "token", "text": note}
    status = {
        "max_tokens": Message.Status.INCOMPLETE,
        "refusal": Message.Status.REFUSED,
    }.get(stop, Message.Status.COMPLETE)
    assistant_msg = save(status, note)
    Conversation.objects.filter(pk=conversation.pk).update(updated_at=timezone.now())
    yield {"type": "done", "message": _serialize(assistant_msg)}
