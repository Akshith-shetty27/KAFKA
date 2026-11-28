import json
from unittest import mock

from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.throttling import ScopedRateThrottle

from apps.assistant.llm import Finished, LLMError, LLMResult, TextDelta
from apps.assistant.models import Conversation, Message
from apps.assistant.services import build_history
from apps.core.testing import auth_client, make_catalog, make_user
from apps.progress.models import ActivityEvent


def read_events(response):
    """Parse an SSE response body into a list of event dicts."""
    body = b"".join(response.streaming_content).decode()
    events = []
    for frame in body.strip().split("\n\n"):
        data = next(line[6:] for line in frame.splitlines() if line.startswith("data: "))
        events.append(json.loads(data))
    return events


class ScriptedProvider:
    """Test double: yields given chunks, then a result or an error."""

    name = "scripted"
    model = "scripted-model"

    def __init__(self, chunks, *, stop="end_turn", error=None):
        self.chunks, self.stop, self.error = chunks, stop, error
        self.calls = []

    def stream(self, *, system, messages, max_tokens):
        self.calls.append({"system": system, "messages": messages})
        for c in self.chunks:
            yield TextDelta(c)
        if self.error:
            raise self.error
        yield Finished(LLMResult(stop_reason=self.stop, model=self.model, input_tokens=10, output_tokens=5))


class ConversationApiTests(APITestCase):
    def setUp(self):
        self.data = make_catalog()
        self.user = make_user()
        self.client = auth_client(self.user)

    def test_requires_login(self):
        self.assertEqual(APIClient().get(reverse("conversation-list")).status_code, 401)
        self.assertEqual(APIClient().get(reverse("assistant-status")).status_code, 401)

    def test_status_reports_offline_demo(self):
        body = self.client.get(reverse("assistant-status")).json()
        self.assertEqual(body["provider"], "fake")
        self.assertTrue(body["offline"])
        self.assertTrue(body["configured"])

    def test_create_general_and_question_conversations(self):
        general = self.client.post(reverse("conversation-list"), {}, format="json")
        self.assertEqual(general.status_code, 201)
        self.assertIsNone(general.json()["question"])
        self.assertEqual(general.json()["capabilities"], {"hint": False, "explain": False, "review": False})

        about = self.client.post(reverse("conversation-list"), {"question_slug": "two-sum"}, format="json").json()
        self.assertEqual(about["question"]["slug"], "two-sum")
        self.assertEqual(about["title"], "Two Sum")
        self.assertTrue(about["capabilities"]["hint"])

    def test_conversation_can_start_with_a_title(self):
        mock = self.client.post(reverse("conversation-list"), {"title": "Mock interview · HR round"}, format="json").json()
        self.assertEqual(mock["title"], "Mock interview · HR round")
        too_long = self.client.post(reverse("conversation-list"), {"title": "x" * 61}, format="json")
        self.assertEqual(too_long.status_code, 400)

    def test_unknown_or_unpublished_question_is_404(self):
        self.assertEqual(self.client.post(reverse("conversation-list"), {"question_slug": "draft-q"}, format="json").status_code, 404)

    def test_list_filter_by_question_and_last_message(self):
        c1 = Conversation.objects.create(user=self.user, question=self.data["questions"]["two_sum"])
        Conversation.objects.create(user=self.user)
        Message.objects.create(conversation=c1, role="user", content="first")
        Message.objects.create(conversation=c1, role="assistant", content="latest reply")
        body = self.client.get(reverse("conversation-list"), {"question": "two-sum"}).json()
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["results"][0]["last_message"]["preview"], "latest reply")

    def test_other_users_conversations_are_invisible(self):
        other = make_user("other@example.com")
        theirs = Conversation.objects.create(user=other, title="private")
        self.assertEqual(self.client.get(reverse("conversation-detail", args=[theirs.pk])).status_code, 404)
        self.assertEqual(self.client.delete(reverse("conversation-detail", args=[theirs.pk])).status_code, 404)
        response = self.client.post(reverse("conversation-messages", args=[theirs.pk]), {"content": "hi"}, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.get(reverse("conversation-list")).json()["count"], 0)
        self.assertTrue(Conversation.objects.filter(pk=theirs.pk).exists())

    def test_delete(self):
        conv = Conversation.objects.create(user=self.user)
        self.assertEqual(self.client.delete(reverse("conversation-detail", args=[conv.pk])).status_code, 204)
        self.assertFalse(Conversation.objects.filter(pk=conv.pk).exists())


class SendMessageTests(APITestCase):
    def setUp(self):
        self.data = make_catalog()
        self.q = self.data["questions"]
        self.user = make_user()
        self.client = auth_client(self.user)
        self.conv = Conversation.objects.create(user=self.user, question=self.q["two_sum"], title="Two Sum")
        self.url = reverse("conversation-messages", args=[self.conv.pk])

    def send(self, **body):
        return self.client.post(self.url, body, format="json", HTTP_ACCEPT="text/event-stream")

    def test_streams_tokens_and_saves_both_messages(self):
        response = self.send(content="Give me a hint", mode="hint", hint_level=2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/event-stream")
        events = read_events(response)
        self.assertEqual(events[0]["type"], "start")
        self.assertEqual(events[0]["user_message"]["hint_level"], 2)
        self.assertEqual(events[-1]["type"], "done")
        streamed = "".join(e["text"] for e in events if e["type"] == "token")
        self.assertIn("hint level 2", streamed)
        self.assertEqual(events[-1]["message"]["content"], streamed)

        msgs = list(self.conv.messages.all())
        self.assertEqual([m.role for m in msgs], ["user", "assistant"])
        self.assertEqual(msgs[1].status, "complete")
        self.assertEqual(msgs[1].provider, "fake")
        self.assertEqual(ActivityEvent.objects.filter(user=self.user, event_type="ai_message").count(), 1)

    def test_general_conversation_gets_title_from_first_message(self):
        conv = Conversation.objects.create(user=self.user)
        url = reverse("conversation-messages", args=[conv.pk])
        read_events(self.client.post(url, {"content": "Explain dynamic programming like I'm new to it"}, format="json"))
        conv.refresh_from_db()
        self.assertEqual(conv.title, "Explain dynamic programming like I'm new to it")

    def test_start_event_carries_conversation_title(self):
        conv = Conversation.objects.create(user=self.user)
        url = reverse("conversation-messages", args=[conv.pk])
        start = read_events(self.client.post(url, {"content": "What is a heap?"}, format="json"))[0]
        self.assertEqual(start["conversation"], {"id": conv.pk, "title": "What is a heap?"})

    def test_validation(self):
        self.assertEqual(self.send(content="   ").status_code, 400)
        self.assertEqual(self.send(content="x" * 4001).status_code, 400)
        self.assertEqual(self.send(content="hi", mode="nonsense").status_code, 400)
        self.assertEqual(self.send(content="hi", mode="hint", hint_level=4).status_code, 400)
        self.assertFalse(self.conv.messages.exists())  # nothing saved on rejected requests

    def test_hint_needs_a_question(self):
        conv = Conversation.objects.create(user=self.user)
        response = self.client.post(reverse("conversation-messages", args=[conv.pk]), {"content": "hint", "mode": "hint"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("mode", response.json()["error"]["fields"])

    def test_explain_on_unanswered_mcq_is_refused(self):
        conv = Conversation.objects.create(user=self.user, question=self.q["pct"])
        response = self.client.post(reverse("conversation-messages", args=[conv.pk]), {"content": "explain", "mode": "explain"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Answer the question first", response.json()["error"]["fields"]["mode"][0])

    def test_provider_error_mid_stream_saves_partial_reply(self):
        provider = ScriptedProvider(["Partial "], error=LLMError("ASK KAFKA is busy right now.", retryable=True))
        with mock.patch("apps.assistant.services.get_provider", return_value=provider):
            events = read_events(self.send(content="hello"))
        self.assertEqual(events[-1]["type"], "error")
        self.assertTrue(events[-1]["retryable"])
        self.assertEqual(events[-1]["saved"]["status"], "error")
        self.assertEqual(self.conv.messages.get(role="assistant").content, "Partial ")

    def test_max_tokens_marks_incomplete_with_note(self):
        with mock.patch("apps.assistant.services.get_provider", return_value=ScriptedProvider(["Long answer"], stop="max_tokens")):
            events = read_events(self.send(content="hello"))
        done = events[-1]["message"]
        self.assertEqual(done["status"], "incomplete")
        self.assertIn("cut short", done["content"])

    def test_refusal_is_saved_as_refused(self):
        with mock.patch("apps.assistant.services.get_provider", return_value=ScriptedProvider([], stop="refusal")):
            events = read_events(self.send(content="something off-topic"))
        self.assertEqual(events[-1]["message"]["status"], "refused")
        self.assertIn("can't help", events[-1]["message"]["content"])

    def test_client_disconnect_keeps_partial_reply(self):
        with mock.patch("apps.assistant.services.get_provider", return_value=ScriptedProvider(["one ", "two ", "three"])):
            response = self.send(content="hello")
            stream = iter(response.streaming_content)
            next(stream)  # start
            next(stream)  # first token
            # The server closes the response iterator when the client goes
            # away; that raises GeneratorExit inside the turn generator.
            # (`streaming_content` is a map over `_iterator`, the test client's
            # closing wrapper, which closes safely without dropping the DB.)
            response._iterator.close()
        reply = self.conv.messages.get(role="assistant")
        self.assertEqual(reply.status, "incomplete")
        self.assertEqual(reply.content, "one ")

    def test_history_is_sent_and_solution_withheld_in_hint_mode(self):
        provider = ScriptedProvider(["ok"])
        with mock.patch("apps.assistant.services.get_provider", return_value=provider):
            read_events(self.send(content="first question"))
            read_events(self.send(content="follow up", mode="hint"))
        call = provider.calls[-1]
        self.assertEqual([t.role for t in call["messages"]], ["user", "assistant", "user"])
        self.assertEqual(call["messages"][-1].content, "follow up")
        self.assertIn("MODE: hint", call["system"])
        self.assertNotIn("Hash it.", call["system"])

    def test_rate_limited(self):
        cache.clear()
        with mock.patch.object(ScopedRateThrottle, "THROTTLE_RATES", {"assistant": "2/min"}):
            codes = [self.send(content=f"msg {i}").status_code for i in range(3)]
        cache.clear()
        self.assertEqual(codes, [200, 200, 429])


class HistoryTests(APITestCase):
    def test_merges_roles_skips_errors_and_starts_with_user(self):
        user = make_user()
        conv = Conversation.objects.create(user=user)
        for role, content, status in [
            ("assistant", "orphan reply", "complete"),
            ("user", "q1", "complete"),
            ("assistant", "broken", "error"),
            ("user", "q1 again", "complete"),
            ("assistant", "answer", "complete"),
        ]:
            Message.objects.create(conversation=conv, role=role, content=content, status=status)
        turns = build_history(conv, limit=20)
        self.assertEqual([(t.role, t.content) for t in turns], [("user", "q1\n\nq1 again"), ("assistant", "answer")])

    def test_character_budget_keeps_newest_messages(self):
        user = make_user()
        conv = Conversation.objects.create(user=user)
        for role, content in [("user", "old " * 50), ("assistant", "older reply " * 50), ("user", "recent question"), ("assistant", "recent answer")]:
            Message.objects.create(conversation=conv, role=role, content=content)
        turns = build_history(conv, limit=20, max_chars=40)
        self.assertEqual([(t.role, t.content) for t in turns], [("user", "recent question"), ("assistant", "recent answer")])

    def test_latest_student_message_is_always_sent(self):
        user = make_user()
        conv = Conversation.objects.create(user=user)
        Message.objects.create(conversation=conv, role="user", content="earlier")
        Message.objects.create(conversation=conv, role="assistant", content="reply")
        Message.objects.create(conversation=conv, role="user", content="a very long new question " * 20)
        turns = build_history(conv, limit=20, max_chars=10)  # budget smaller than the new message
        self.assertEqual(len(turns), 1)
        self.assertTrue(turns[0].content.startswith("a very long new question"))
