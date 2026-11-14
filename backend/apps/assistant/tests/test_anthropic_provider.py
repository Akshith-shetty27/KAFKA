"""The Claude adapter, tested against a stub client — no network, no cost."""

from types import SimpleNamespace

import anthropic
import httpx2
from django.test import SimpleTestCase

from apps.assistant.llm import ChatTurn, Finished, LLMError, TextDelta
from apps.assistant.llm.anthropic_provider import FALLBACK_BETA, AnthropicProvider


class StubStream:
    def __init__(self, texts, final):
        self.text_stream = iter(texts)
        self._final = final

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self._final


class StubClient:
    def __init__(self, *, texts=(), final=None, error=None):
        self.kwargs = None
        self._texts, self._final, self._error = texts, final, error
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self._stream))

    def _stream(self, **kwargs):
        self.kwargs = kwargs
        if self._error:
            raise self._error
        return StubStream(self._texts, self._final)


def final_message(stop_reason="end_turn"):
    usage = SimpleNamespace(input_tokens=120, output_tokens=40, cache_read_input_tokens=100)
    return SimpleNamespace(stop_reason=stop_reason, model="claude-opus-5-5", usage=usage)


def api_error(cls, status):
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    return cls("boom", response=httpx2.Response(status, request=request), body=None)


class AnthropicProviderTests(SimpleTestCase):
    def run_stream(self, client):
        provider = AnthropicProvider(model="claude-opus-5-5", effort="medium", client=client)
        return list(provider.stream(system="SYS", messages=[ChatTurn("user", "hi")], max_tokens=1000))

    def test_request_shape(self):
        client = StubClient(texts=["Hel", "lo"], final=final_message())
        events = self.run_stream(client)
        kw = client.kwargs
        self.assertEqual(kw["model"], "claude-opus-5-5")
        self.assertEqual(kw["system"], "SYS")
        self.assertEqual(kw["messages"], [{"role": "user", "content": "hi"}])
        self.assertEqual(kw["output_config"], {"effort": "medium"})
        self.assertEqual(kw["cache_control"], {"type": "ephemeral"})
        self.assertEqual(kw["betas"], [FALLBACK_BETA])
        self.assertEqual(kw["fallbacks"], "default")
        self.assertNotIn("thinking", kw)  # adaptive by default on this model

        self.assertEqual([e.text for e in events if isinstance(e, TextDelta)], ["Hel", "lo"])
        result = events[-1].result
        self.assertIsInstance(events[-1], Finished)
        self.assertEqual((result.input_tokens, result.output_tokens, result.cache_read_tokens), (120, 40, 100))

    def test_refusal_stop_reason_passes_through(self):
        events = self.run_stream(StubClient(texts=[], final=final_message("refusal")))
        self.assertEqual(events[-1].result.stop_reason, "refusal")

    def test_errors_become_safe_messages(self):
        cases = [
            (api_error(anthropic.RateLimitError, 429), True, "busy"),
            (api_error(anthropic.AuthenticationError, 401), False, "configured"),
            (api_error(anthropic.InternalServerError, 500), True, "problem"),
            (anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com")), True, "reach"),
        ]
        for error, retryable, phrase in cases:
            with self.subTest(error=type(error).__name__):
                with self.assertRaises(LLMError) as ctx:
                    self.run_stream(StubClient(error=error))
                self.assertEqual(ctx.exception.retryable, retryable)
                self.assertIn(phrase, ctx.exception.user_message)
                self.assertNotIn("boom", ctx.exception.user_message)  # provider details never reach the student
