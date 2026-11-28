"""
The provider-agnostic interface. Nothing outside `apps/assistant/llm/` knows
which LLM vendor is in use — swapping providers means adding an adapter here
and changing LLM_PROVIDER in the environment.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True)
class ChatTurn:
    role: Literal["user", "assistant"]
    content: str


@dataclass(frozen=True)
class LLMResult:
    stop_reason: str  # "end_turn" | "max_tokens" | "refusal" | provider-specific
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cache_read_tokens: int | None = None


@dataclass(frozen=True)
class ResearchResult:
    """What a web-research call found: a plain-text report and the sites it came from."""

    text: str
    sources: list[str]  # friendly site names taken from the real result URLs (e.g. "GeeksforGeeks")
    result: LLMResult


@dataclass(frozen=True)
class TextDelta:
    text: str


@dataclass(frozen=True)
class Finished:
    result: LLMResult


StreamEvent = TextDelta | Finished


class LLMError(Exception):
    """A provider failure, translated into something safe to show a student."""

    def __init__(self, user_message: str, *, retryable: bool, detail: str = ""):
        super().__init__(detail or user_message)
        self.user_message = user_message
        self.retryable = retryable


class LLMProvider(Protocol):
    name: str
    model: str
    configured: bool  # credentials present (False → the UI explains why ASK KAFKA can't answer)

    def stream(self, *, system: str, messages: list[ChatTurn], max_tokens: int) -> Iterator[StreamEvent]:
        """Yield TextDelta events as text arrives, then exactly one Finished.

        Raises LLMError on provider failures (possibly after some deltas).
        """
        ...

    def complete_json(
        self, *, system: str, prompt: str, schema: dict, name: str, max_tokens: int, effort: str | None = None,
        patient: bool = False,
    ) -> tuple[dict, LLMResult]:
        """One non-streaming request whose reply must match `schema` (JSON Schema).

        Used for structured features (e.g. study plans), where the result is
        validated and stored rather than shown as it arrives. Returns the
        parsed object. `effort` overrides the provider's reasoning effort for
        this call. `patient` lets the call wait out a short rate limit (used
        right after a research call has spent part of the minute's budget).
        Raises LLMError on provider failures, on a reply cut off by
        `max_tokens`, or on output that isn't valid JSON — callers must still
        validate the content itself.
        """
        ...

    # Optional capability: providers that can search the web set this to True
    # and implement `research(system, prompt, max_tokens) -> ResearchResult`.
    supports_research: bool


def parse_json_reply(text: str, stop_reason: str) -> dict:
    """Shared tail of every `complete_json`: turn the reply text into a dict or fail clearly."""
    import json

    if stop_reason == "max_tokens":
        raise LLMError("KAFKA ran out of room before finishing. Please try again.", retryable=True, detail="max_tokens")
    if stop_reason == "refusal":
        raise LLMError("KAFKA can't help with that request.", retryable=False, detail="refusal")
    try:
        data = json.loads(text)
    except (TypeError, ValueError) as exc:
        raise LLMError("KAFKA returned an unreadable answer. Please try again.", retryable=True, detail=str(exc)) from exc
    if not isinstance(data, dict):
        raise LLMError("KAFKA returned an unreadable answer. Please try again.", retryable=True, detail="not an object")
    return data
