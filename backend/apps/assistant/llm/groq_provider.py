"""
Groq adapter (official `groq` SDK) — the default provider.

Model: `openai/gpt-oss-120b` (LLM_MODEL). Groq offers a free tier for it, so
ASK KAFKA costs nothing to run while usage stays inside the free limits.

Free-tier limits are per Groq account — i.e. shared by *every* student using
this deployment (check the Limits page in the Groq console; at the time of
writing roughly 30 requests/min, 1,000 requests/day, 8,000 tokens/min and
200,000 tokens/day for this model). That is why the defaults here are
deliberately small: replies are capped at 3,000 tokens and
`reasoning_effort` defaults to medium. When the limit is hit, Groq answers
429 and the student sees "busy, try again in a minute".

Notes:
- GPT-OSS is a reasoning model. `include_reasoning=False` keeps its private
  reasoning out of the response, so students only ever see the answer.
- Prompt caching is automatic on Groq (no parameter); our prompt puts the
  stable instructions first so cache hits are likely.
- The API key is read by the SDK from GROQ_API_KEY — backend only.
"""

import logging
import os
from collections.abc import Iterator

import groq

from .base import ChatTurn, Finished, LLMError, LLMResult, StreamEvent, TextDelta

logger = logging.getLogger(__name__)

# Groq's GPT-OSS accepts low | medium | high. Map the wider vocabulary used by
# other providers onto it so LLM_EFFORT means the same thing everywhere.
EFFORT_MAP = {"low": "low", "medium": "medium", "high": "high", "xhigh": "high", "max": "high"}
# Our stop vocabulary is provider-neutral (see services.STOP_NOTES).
FINISH_MAP = {"stop": "end_turn", "length": "max_tokens", "content_filter": "refusal"}


def _usage_from(chunk):
    usage = getattr(chunk, "usage", None)
    if usage is None and getattr(chunk, "x_groq", None) is not None:
        usage = chunk.x_groq.usage
    return usage


class GroqProvider:
    name = "groq"

    def __init__(self, *, model: str, effort: str, timeout: float = 60.0, client=None):
        self.model = model
        self.effort = EFFORT_MAP.get(effort, "medium")
        self._timeout = timeout
        self._client = client

    @property
    def configured(self) -> bool:
        return self._client is not None or bool(os.environ.get("GROQ_API_KEY"))

    def _get_client(self):
        # Created lazily: a missing key should give students a clear message,
        # not crash the server at startup.
        if self._client is None:
            if not os.environ.get("GROQ_API_KEY"):
                raise LLMError("ASK KAFKA isn't configured yet (no GROQ_API_KEY on the server).", retryable=False)
            # One retry only: on the free tier a 429 usually means "wait for the
            # next minute", and long silent retries would leave the student waiting.
            self._client = groq.Groq(timeout=self._timeout, max_retries=1)
        return self._client

    def stream(self, *, system: str, messages: list[ChatTurn], max_tokens: int) -> Iterator[StreamEvent]:
        finish_reason = None
        usage = None
        model = self.model
        client = self._get_client()
        try:
            stream = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system}]
                + [{"role": m.role, "content": m.content} for m in messages],
                max_completion_tokens=max_tokens,
                reasoning_effort=self.effort,
                include_reasoning=False,
                stream=True,
            )
            for chunk in stream:
                model = getattr(chunk, "model", None) or model
                usage = _usage_from(chunk) or usage
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                if choice.delta and choice.delta.content:
                    yield TextDelta(choice.delta.content)
                if choice.finish_reason:
                    finish_reason = choice.finish_reason
        except groq.AuthenticationError as exc:
            logger.error("Groq authentication failed: %s", exc)
            raise LLMError("ASK KAFKA isn't configured correctly yet.", retryable=False, detail=str(exc)) from exc
        except groq.PermissionDeniedError as exc:
            logger.error("Groq permission denied: %s", exc)
            raise LLMError("ASK KAFKA isn't configured correctly yet.", retryable=False, detail=str(exc)) from exc
        except groq.RateLimitError as exc:
            logger.warning("Groq rate limit reached: %s", exc)
            raise LLMError(
                "ASK KAFKA is busy right now (free-tier limit reached). Try again in a minute.",
                retryable=True,
                detail=str(exc),
            ) from exc
        except (groq.APIConnectionError, groq.APITimeoutError) as exc:
            raise LLMError("Couldn't reach ASK KAFKA. Check your connection and try again.", retryable=True, detail=str(exc)) from exc
        except (groq.BadRequestError, groq.UnprocessableEntityError) as exc:
            logger.error("Groq rejected the request: %s", exc)
            raise LLMError("ASK KAFKA couldn't process that message.", retryable=False, detail=str(exc)) from exc
        except groq.APIStatusError as exc:
            logger.warning("Groq API error %s: %s", exc.status_code, exc)
            raise LLMError(
                "ASK KAFKA had a problem answering. Please try again.",
                retryable=exc.status_code >= 500 or exc.status_code == 413,
                detail=str(exc),
            ) from exc

        details = getattr(usage, "prompt_tokens_details", None) if usage else None
        yield Finished(
            LLMResult(
                stop_reason=FINISH_MAP.get(finish_reason, "end_turn"),
                model=model,
                input_tokens=getattr(usage, "prompt_tokens", None),
                output_tokens=getattr(usage, "completion_tokens", None),
                cache_read_tokens=getattr(details, "cached_tokens", None) if details else None,
            )
        )
