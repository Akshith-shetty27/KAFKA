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
