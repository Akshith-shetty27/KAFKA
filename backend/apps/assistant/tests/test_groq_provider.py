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


class JsonStubClient:
    """Non-streaming stub: returns queued responses / raises queued errors in order."""

    def __init__(self, *outcomes):
        self.calls = []
        self._outcomes = list(outcomes)
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def with_options(self, **options):
        self.options = options
        return self


def json_response(content, finish="stop"):
    message = SimpleNamespace(content=content)
    return SimpleNamespace(
        model="openai/gpt-oss-120b",
        choices=[SimpleNamespace(message=message, finish_reason=finish)],
        usage=usage(prompt=2000, completion=3000, cached=0),
    )


def bad_request(message):
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    return groq.BadRequestError(message, response=httpx.Response(400, request=request), body=None)


class GroqJsonTests(SimpleTestCase):
    SCHEMA = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"], "additionalProperties": False}

    def call(self, client, **kwargs):
        provider = GroqProvider(model="openai/gpt-oss-120b", effort="medium", client=client)
        return provider.complete_json(system="sys", prompt="hi", schema=self.SCHEMA, name="test", max_tokens=4500, **kwargs)

    def test_request_shape_uses_strict_schema_and_effort_override(self):
        client = JsonStubClient(json_response('{"ok": true}'))
        data, result = self.call(client, effort="low")
        self.assertEqual(data, {"ok": True})
        self.assertEqual((result.input_tokens, result.output_tokens, result.stop_reason), (2000, 3000, "end_turn"))
        kwargs = client.calls[0]
        self.assertEqual(kwargs["response_format"], {
            "type": "json_schema", "json_schema": {"name": "test", "schema": self.SCHEMA, "strict": True},
        })
        self.assertEqual((kwargs["reasoning_effort"], kwargs["max_completion_tokens"]), ("low", 4500))
        self.assertIs(kwargs["include_reasoning"], False)
        self.assertNotIn("stream", kwargs)
        self.assertEqual(kwargs["messages"], [{"role": "system", "content": "sys"}, {"role": "user", "content": "hi"}])

    def test_default_effort_is_the_providers(self):
        client = JsonStubClient(json_response('{"ok": true}'))
        self.call(client)
        self.assertEqual(client.calls[0]["reasoning_effort"], "medium")

    def test_schema_validation_failure_is_retried_once(self):
        client = JsonStubClient(bad_request("json_validate_failed"), json_response('{"ok": false}'))
        data, _ = self.call(client)
        self.assertEqual(data, {"ok": False})
        self.assertEqual(len(client.calls), 2)

        client = JsonStubClient(bad_request("json_validate_failed"), bad_request("json_validate_failed"))
        with self.assertRaises(LLMError) as ctx:
            self.call(client)
        self.assertTrue(ctx.exception.retryable)
        self.assertEqual(len(client.calls), 2)

    def test_other_bad_requests_are_not_retried(self):
        client = JsonStubClient(bad_request("invalid model"))
        with self.assertRaises(LLMError) as ctx:
            self.call(client)
        self.assertFalse(ctx.exception.retryable)
        self.assertEqual(len(client.calls), 1)

    def test_truncated_or_unreadable_replies_are_retryable_errors(self):
        for response in (json_response('{"ok": tr', finish="length"), json_response("not json"), json_response("[1, 2]")):
            with self.subTest(content=response.choices[0].message.content), self.assertRaises(LLMError) as ctx:
                self.call(JsonStubClient(response))
            self.assertTrue(ctx.exception.retryable)

    def test_request_larger_than_the_minute_budget_is_explained(self):
        with self.assertRaises(LLMError) as ctx:
            self.call(JsonStubClient(status_error(groq.APIStatusError, 413)))
        self.assertIn("too large", ctx.exception.user_message)
        self.assertTrue(ctx.exception.retryable)


class FakeJsonTests(SimpleTestCase):
    def test_builds_a_schema_shaped_object_quoting_the_prompt(self):
        from apps.assistant.llm.fake_provider import FakeProvider
        from apps.prep.schema import plan_schema

        prompt = "<job_description>\nShort\nWe need strong SQL and REST API skills for this role.\n</job_description>"
        data, result = FakeProvider().complete_json(system="", prompt=prompt, schema=plan_schema(), name="plan", max_tokens=10)
        self.assertEqual(set(data), {"is_job_description", "rejection_reason", "summary", "research", "requirements", "sections"})
        self.assertEqual(data["requirements"][0]["evidence"], "We need strong SQL and REST API skills for this role.")
        self.assertIn(data["sections"][0]["kind"], ("coding", "aptitude", "core_cs", "interview"))
        self.assertEqual(result.model, "kafka-offline-demo")


class GroqResearchTests(SimpleTestCase):
    def provider(self, client):
        return GroqProvider(model="openai/gpt-oss-120b", effort="medium", client=client)

    def test_research_uses_browser_search_and_returns_clean_text_and_real_sources(self):
        message = SimpleNamespace(
            content="Rounds: OA 【0†L1-L4】, technical. More at https://example.com/x",
            executed_tools=[{"type": "browser.open", "search_results": {"results": [{"url": "https://www.geeksforgeeks.org/a"}]}}],
        )
        response = SimpleNamespace(model="openai/gpt-oss-120b", choices=[SimpleNamespace(message=message, finish_reason="stop")],
                                   usage=usage(prompt=4000, completion=300, cached=0))
        client = JsonStubClient(response)
        found = self.provider(client).research(system="sys", prompt="find", max_tokens=1500)
        self.assertEqual(client.calls[0]["tools"], [{"type": "browser_search"}])
        self.assertEqual(client.calls[0]["reasoning_effort"], "low")
        self.assertEqual(found.text, "Rounds: OA , technical. More at")
        self.assertEqual(found.sources, ["GeeksforGeeks"])
        self.assertEqual(found.result.input_tokens, 4000)

    def test_research_failures_become_llm_errors(self):
        client = JsonStubClient(status_error(groq.APIStatusError, 503))
        with self.assertRaises(LLMError):
            self.provider(client).research(system="sys", prompt="find", max_tokens=1500)

    def test_patient_json_calls_allow_more_retries_for_the_rate_limit(self):
        client = JsonStubClient(json_response('{"ok": true}'))
        self.provider(client).complete_json(system="s", prompt="p", schema=GroqJsonTests.SCHEMA, name="t",
                                            max_tokens=100, patient=True)
        self.assertEqual(client.options, {"max_retries": 3})
