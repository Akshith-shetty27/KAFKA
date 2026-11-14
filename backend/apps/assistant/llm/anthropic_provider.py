"""
Claude adapter (official `anthropic` SDK).

Choices, all overridable from the environment:
- model `claude-opus-5-5` (LLM_MODEL), effort `medium` (LLM_EFFORT). Thinking is
  adaptive on this model and can't be turned off; effort controls depth/cost.
- Streaming, so long answers never hit HTTP timeouts and tokens reach the
  student as they're generated.
- Automatic prompt caching (`cache_control`), so the system prompt + earlier
  turns are cheaper on every follow-up in a conversation.
- Server-side refusal fallbacks (`fallbacks="default"`): if the model declines
  a request on a safety classifier, the API retries it on a fallback model
  within the same call. A final `stop_reason == "refusal"` means every model
  declined; that's surfaced as a polite message.
The API key is read by the SDK from ANTHROPIC_API_KEY — it never leaves the
backend.
"""

import logging
from collections.abc import Iterator

import anthropic

from .base import ChatTurn, Finished, LLMError, LLMResult, StreamEvent, TextDelta

logger = logging.getLogger(__name__)

FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AnthropicProvider:
    name = "anthropic"
    configured = True  # the SDK resolves credentials itself (env var or `ant` profile)

    def __init__(self, *, model: str, effort: str, timeout: float = 120.0, client=None):
        self.model = model
        self.effort = effort
        self._client = client or anthropic.Anthropic(timeout=timeout, max_retries=2)

    def stream(self, *, system: str, messages: list[ChatTurn], max_tokens: int) -> Iterator[StreamEvent]:
        try:
            with self._client.beta.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                output_config={"effort": self.effort},
                cache_control={"type": "ephemeral"},
                betas=[FALLBACK_BETA],
                fallbacks="default",
            ) as stream:
                for text in stream.text_stream:
                    yield TextDelta(text)
                final = stream.get_final_message()
        except anthropic.AuthenticationError as exc:
            logger.error("Anthropic authentication failed: %s", exc)
            raise LLMError("ASK KAFKA isn't configured correctly yet.", retryable=False, detail=str(exc)) from exc
        except anthropic.PermissionDeniedError as exc:
            logger.error("Anthropic permission denied: %s", exc)
            raise LLMError("ASK KAFKA isn't configured correctly yet.", retryable=False, detail=str(exc)) from exc
        except anthropic.RateLimitError as exc:
            raise LLMError("ASK KAFKA is busy right now. Try again in a minute.", retryable=True, detail=str(exc)) from exc
        except (anthropic.APIConnectionError, anthropic.APITimeoutError) as exc:
            raise LLMError("Couldn't reach ASK KAFKA. Check your connection and try again.", retryable=True, detail=str(exc)) from exc
        except anthropic.BadRequestError as exc:
            logger.error("Anthropic rejected the request: %s", exc)
            raise LLMError("ASK KAFKA couldn't process that message.", retryable=False, detail=str(exc)) from exc
        except anthropic.APIStatusError as exc:
            logger.warning("Anthropic API error %s: %s", exc.status_code, exc)
            raise LLMError("ASK KAFKA had a problem answering. Please try again.", retryable=exc.status_code >= 500, detail=str(exc)) from exc

        usage = final.usage
        yield Finished(
            LLMResult(
                stop_reason=final.stop_reason or "end_turn",
                model=final.model,
                input_tokens=getattr(usage, "input_tokens", None),
                output_tokens=getattr(usage, "output_tokens", None),
                cache_read_tokens=getattr(usage, "cache_read_input_tokens", None),
            )
        )
