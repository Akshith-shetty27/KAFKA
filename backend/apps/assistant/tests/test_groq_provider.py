"""The Groq adapter, tested against a stub client — no API key, no network."""

import os
from types import SimpleNamespace
from unittest import mock

import groq
import httpx
from django.test import SimpleTestCase, override_settings

from apps.assistant.llm import ChatTurn, Finished, LLMError, TextDelta, registry
from apps.assistant.llm.groq_provider import GroqProvider


def chunk(text=None, finish=None, usage=None, model="openai/gpt-oss-120b"):
    choice = SimpleNamespace(delta=SimpleNamespace(content=text), finish_reason=finish)
    return SimpleNamespace(model=model, choices=[choice], usage=None, x_groq=SimpleNamespace(usage=usage) if usage else None)


def usage(prompt=900, completion=120, cached=600):
    return SimpleNamespace(prompt_tokens=prompt, completion_tokens=completion, prompt_tokens_details=SimpleNamespace(cached_tokens=cached))


class StubClient:
    def __init__(self, *, chunks=(), error=None):
        self.kwargs = None
        self._chunks, self._error = chunks, error
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.kwargs = kwargs
        if self._error:
            raise self._error
        return iter(self._chunks)


def status_error(cls, status):
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    return cls("boom", response=httpx.Response(status, request=request), body=None)


class GroqProviderTests(SimpleTestCase):
    def run_stream(self, client, effort="medium"):
        provider = GroqProvider(model="openai/gpt-oss-120b", effort=effort, client=client)
        return list(provider.stream(system="SYS", messages=[ChatTurn("user", "hi")], max_tokens=3000))

    def test_request_shape_and_streaming(self):
        client = StubClient(chunks=[chunk("Hel"), chunk("lo"), chunk(None, finish="stop", usage=usage())])
        events = self.run_stream(client)
        kw = client.kwargs
        self.assertEqual(kw["model"], "openai/gpt-oss-120b")
        self.assertEqual(kw["messages"], [{"role": "system", "content": "SYS"}, {"role": "user", "content": "hi"}])
        self.assertEqual(kw["max_completion_tokens"], 3000)
        self.assertEqual(kw["reasoning_effort"], "medium")
        self.assertIs(kw["include_reasoning"], False)  # students never see the model's private reasoning
        self.assertIs(kw["stream"], True)

        self.assertEqual([e.text for e in events if isinstance(e, TextDelta)], ["Hel", "lo"])
        self.assertIsInstance(events[-1], Finished)
        result = events[-1].result
        self.assertEqual(result.stop_reason, "end_turn")
        self.assertEqual((result.input_tokens, result.output_tokens, result.cache_read_tokens), (900, 120, 600))

    def test_effort_is_mapped_to_groq_values(self):
        for ours, theirs in [("low", "low"), ("high", "high"), ("max", "high"), ("nonsense", "medium")]:
            client = StubClient(chunks=[chunk(None, finish="stop")])
            self.run_stream(client, effort=ours)
            self.assertEqual(client.kwargs["reasoning_effort"], theirs, ours)

    def test_finish_reasons_map_to_shared_vocabulary(self):
        for finish, expected in [("length", "max_tokens"), ("content_filter", "refusal"), (None, "end_turn")]:
            events = self.run_stream(StubClient(chunks=[chunk("x", finish=finish)]))
            self.assertEqual(events[-1].result.stop_reason, expected, finish)

    def test_errors_become_safe_messages(self):
        cases = [
            (status_error(groq.RateLimitError, 429), True, "free-tier limit"),
            (status_error(groq.AuthenticationError, 401), False, "configured"),
            (status_error(groq.BadRequestError, 400), False, "couldn't process"),
            (status_error(groq.InternalServerError, 503), True, "problem"),
            (groq.APIConnectionError(request=httpx.Request("POST", "https://api.groq.com")), True, "reach"),
        ]
        for error, retryable, phrase in cases:
            with self.subTest(error=type(error).__name__):
                with self.assertRaises(LLMError) as ctx:
                    self.run_stream(StubClient(error=error))
                self.assertEqual(ctx.exception.retryable, retryable)
                self.assertIn(phrase, ctx.exception.user_message)
                self.assertNotIn("boom", ctx.exception.user_message)

    def test_missing_key_is_a_clear_error_not_a_crash(self):
        with mock.patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            provider = GroqProvider(model="openai/gpt-oss-120b", effort="medium")
            self.assertFalse(provider.configured)
            with self.assertRaises(LLMError) as ctx:
                list(provider.stream(system="S", messages=[ChatTurn("user", "hi")], max_tokens=100))
        self.assertFalse(ctx.exception.retryable)
        self.assertIn("GROQ_API_KEY", ctx.exception.user_message)

    def test_configured_when_key_present(self):
        with mock.patch.dict(os.environ, {"GROQ_API_KEY": "gsk_test"}):
            self.assertTrue(GroqProvider(model="m", effort="medium").configured)


class RegistryDefaultsTests(SimpleTestCase):
    def tearDown(self):
        registry.get_provider.cache_clear()

    def test_groq_is_default_with_gpt_oss_and_small_reply_cap(self):
        with override_settings(LLM_PROVIDER="groq", LLM_MODEL="", LLM_MAX_TOKENS=0):
            registry.get_provider.cache_clear()
            provider = registry.get_provider()
            self.assertEqual(provider.name, "groq")
            self.assertEqual(provider.model, "openai/gpt-oss-120b")
            self.assertEqual(registry.max_reply_tokens(), 3000)

    def test_env_overrides_win(self):
        with override_settings(LLM_PROVIDER="groq", LLM_MODEL="openai/gpt-oss-20b", LLM_MAX_TOKENS=1500):
            registry.get_provider.cache_clear()
            self.assertEqual(registry.get_provider().model, "openai/gpt-oss-20b")
            self.assertEqual(registry.max_reply_tokens(), 1500)

    def test_unknown_provider_is_rejected(self):
        from django.core.exceptions import ImproperlyConfigured

        with override_settings(LLM_PROVIDER="mystery", LLM_MODEL=""):
            registry.get_provider.cache_clear()
            with self.assertRaises(ImproperlyConfigured):
                registry.get_provider()
