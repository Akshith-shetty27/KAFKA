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
import re
from collections.abc import Iterator
from urllib.parse import urlparse

import groq

from .base import ChatTurn, Finished, LLMError, LLMResult, ResearchResult, StreamEvent, TextDelta, parse_json_reply

logger = logging.getLogger(__name__)

# Groq's GPT-OSS accepts low | medium | high. Map the wider vocabulary used by
# other providers onto it so LLM_EFFORT means the same thing everywhere.
EFFORT_MAP = {"low": "low", "medium": "medium", "high": "high", "xhigh": "high", "max": "high"}
# Our stop vocabulary is provider-neutral (see services.STOP_NOTES).
FINISH_MAP = {"stop": "end_turn", "length": "max_tokens", "content_filter": "refusal"}


# Friendly names for sites that interview experiences usually come from.
SITE_NAMES = {
    "geeksforgeeks": "GeeksforGeeks", "glassdoor": "Glassdoor", "leetcode": "LeetCode", "ambitionbox": "AmbitionBox",
    "reddit": "Reddit", "indeed": "Indeed", "interviewbit": "InterviewBit", "prepinsta": "PrepInsta",
    "naukri": "Naukri", "medium": "Medium", "linkedin": "LinkedIn", "youtube": "YouTube", "quora": "Quora",
    "teamblind": "Blind", "levels": "Levels.fyi", "codingninjas": "Coding Ninjas", "takeuforward": "takeUforward",
}
# Search engines and the like: the tool's own plumbing, not sources.
NOT_SOURCES = {"exa", "bing", "google", "duckduckgo", "search", "brave"}
_CITATION = re.compile(r"【[^】]*】")
_URL = re.compile(r"https?://\S+")


def site_name(url: str) -> str | None:
    """'https://www.geeksforgeeks.org/x' → 'GeeksforGeeks'; unknown sites → their capitalised name."""
    host = (urlparse(url).hostname or "").lower().removeprefix("www.")
    if not host:
        return None
    parts = host.split(".")
    # Skip second-level suffixes like .co.in / .com.au / .ac.uk to reach the site's own name.
    if len(parts) >= 3 and parts[-2] in {"co", "com", "org", "net", "ac", "gov", "edu"}:
        parts = parts[:-1]
    key = parts[-2] if len(parts) >= 2 else parts[0]
    if key in NOT_SOURCES:
        return None
    return SITE_NAMES.get(key, key.capitalize())


def sources_from(executed_tools) -> list[str]:
    """Site names of the pages the model opened first, then of the top search hits (max 5)."""
    opened, searched = [], []
    for tool in executed_tools or []:
        data = tool.model_dump() if hasattr(tool, "model_dump") else dict(tool)
        results = (data.get("search_results") or {}).get("results") or []
        target = opened if "open" in str(data.get("type", "")) else searched
        target += [r.get("url", "") for r in results[: (1 if target is opened else 4)]]
    names = [site_name(u) for u in opened + searched]
    return list(dict.fromkeys(n for n in names if n))[:5]


def clean_research_text(text: str) -> str:
    """Drop the model's citation markers and any raw URLs — students never get sent off-site."""
    text = _URL.sub("", _CITATION.sub("", text or ""))
    text = re.sub(r"[ \t]{2,}", " ", text)
    return re.sub(r"[ \t]+\n", "\n", text).strip()


def _usage_from(chunk):
    usage = getattr(chunk, "usage", None)
    if usage is None and getattr(chunk, "x_groq", None) is not None:
        usage = chunk.x_groq.usage
    return usage


def _to_llm_error(exc: Exception) -> LLMError:
    """Translate an SDK exception into a message that is safe to show a student."""
    if isinstance(exc, (groq.AuthenticationError, groq.PermissionDeniedError)):
        logger.error("Groq rejected our credentials: %s", exc)
        return LLMError("ASK KAFKA isn't configured correctly yet.", retryable=False, detail=str(exc))
    if isinstance(exc, groq.RateLimitError):
        logger.warning("Groq rate limit reached: %s", exc)
        return LLMError(
            "ASK KAFKA is busy right now (free-tier limit reached). Try again in a minute.",
            retryable=True,
            detail=str(exc),
        )
    if isinstance(exc, (groq.APIConnectionError, groq.APITimeoutError)):
        return LLMError("Couldn't reach ASK KAFKA. Check your connection and try again.", retryable=True, detail=str(exc))
    if isinstance(exc, (groq.BadRequestError, groq.UnprocessableEntityError)):
        logger.error("Groq rejected the request: %s", exc)
        if "json_validate_failed" in str(exc):  # structured output didn't match the schema
            return LLMError("KAFKA returned an incomplete answer. Please try again.", retryable=True, detail=str(exc))
        return LLMError("ASK KAFKA couldn't process that message.", retryable=False, detail=str(exc))
    if isinstance(exc, groq.APIStatusError):
        logger.warning("Groq API error %s: %s", exc.status_code, exc)
        if exc.status_code == 413:  # request + reply budget larger than the per-minute token limit
            return LLMError(
                "That request is too large for ASK KAFKA's free-tier limit right now. Try again in a minute.",
                retryable=True,
                detail=str(exc),
            )
        return LLMError(
            "ASK KAFKA had a problem answering. Please try again.",
            retryable=exc.status_code >= 500,
            detail=str(exc),
        )
    logger.exception("Unexpected Groq error")
    return LLMError("ASK KAFKA had a problem answering. Please try again.", retryable=True, detail=str(exc))


class GroqProvider:
    name = "groq"
    supports_research = True  # Groq's built-in browser_search tool (gpt-oss models)

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
        except groq.GroqError as exc:
            raise _to_llm_error(exc) from exc

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

    def complete_json(
        self, *, system: str, prompt: str, schema: dict, name: str, max_tokens: int, effort: str | None = None,
        patient: bool = False,
    ) -> tuple[dict, LLMResult]:
        # Strict structured outputs: Groq constrains decoding to the schema
        # (supported on gpt-oss models; not available with streaming).
        # Groq checks the finished output against the schema and answers 400
        # json_validate_failed when it doesn't match; that is a sampling fluke,
        # so it is retried once before giving up.
        client = self._get_client()
        if patient:
            # Right after a research call the minute's token budget may be spent;
            # the SDK then waits out Groq's retry-after (≤ 60 s) and tries again.
            client = client.with_options(max_retries=3)
        for attempt in (1, 2):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                    max_completion_tokens=max_tokens,
                    reasoning_effort=EFFORT_MAP.get(effort, self.effort) if effort else self.effort,
                    include_reasoning=False,
                    response_format={"type": "json_schema", "json_schema": {"name": name, "schema": schema, "strict": True}},
                )
                break
            except groq.BadRequestError as exc:
                if attempt == 1 and "json_validate_failed" in str(exc):
                    logger.warning("Groq output failed schema validation; retrying once")
                    continue
                raise _to_llm_error(exc) from exc
            except groq.GroqError as exc:
                raise _to_llm_error(exc) from exc

        choice = response.choices[0]
        usage = response.usage
        details = getattr(usage, "prompt_tokens_details", None) if usage else None
        result = LLMResult(
            stop_reason=FINISH_MAP.get(choice.finish_reason, "end_turn"),
            model=getattr(response, "model", None) or self.model,
            input_tokens=getattr(usage, "prompt_tokens", None),
            output_tokens=getattr(usage, "completion_tokens", None),
            cache_read_tokens=getattr(details, "cached_tokens", None) if details else None,
        )
        return parse_json_reply(choice.message.content, result.stop_reason), result

    def research(self, *, system: str, prompt: str, max_tokens: int) -> ResearchResult:
        """Search the web with Groq's built-in browser_search tool and report back in plain text.

        Search results are added to the prompt by Groq, so one call costs a few
        thousand input tokens — this is the expensive step of plan generation.
        """
        client = self._get_client()
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                tools=[{"type": "browser_search"}],
                max_completion_tokens=max_tokens,
                reasoning_effort="low",
                include_reasoning=False,
            )
        except groq.GroqError as exc:
            raise _to_llm_error(exc) from exc
        message = response.choices[0].message
        usage = response.usage
        return ResearchResult(
            text=clean_research_text(message.content),
            sources=sources_from(getattr(message, "executed_tools", None)),
            result=LLMResult(
                stop_reason=FINISH_MAP.get(response.choices[0].finish_reason, "end_turn"),
                model=getattr(response, "model", None) or self.model,
                input_tokens=getattr(usage, "prompt_tokens", None),
                output_tokens=getattr(usage, "completion_tokens", None),
            ),
        )
