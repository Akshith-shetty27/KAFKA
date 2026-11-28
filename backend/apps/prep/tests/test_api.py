"""Study-plan API: generation, ownership, progress — with stub providers (no network)."""

from unittest import mock

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from apps.assistant.llm import LLMError, LLMResult, ResearchResult
from apps.assistant.llm.fake_provider import FakeProvider
from apps.catalog.models import Pattern
from apps.core.testing import auth_client, make_catalog, make_user
from apps.prep.models import PlanItem, PreparationPlan
from apps.progress.models import QuestionProgress

from .test_services import item, reply, requirement, section

URL = "/api/v1/prep/plans/"
JD = (
    "Backend Engineer at Acme.\n"
    "Design and implement RESTful APIs in Python and Django.\n"
    "Write efficient SQL queries on PostgreSQL and understand indexing.\n"
    "Strong fundamentals in data structures and algorithms, especially arrays and hash maps.\n"
    "Nice to have: Docker and AWS. Interview: online assessment with aptitude, then two technical rounds."
)


class StubProvider:
    name = "stub"
    model = "stub-model"
    configured = True
    supports_research = True

    def __init__(self, data=None, error=None, research_text="Company found: Acme\nBasis: company\nRounds: online assessment, then two technical rounds."):
        self.data, self.error, self.research_text = data, error, research_text
        self.calls, self.research_calls = [], []

    def research(self, **kwargs):
        self.research_calls.append(kwargs)
        return ResearchResult(text=self.research_text, sources=["GeeksforGeeks", "Glassdoor"],
                              result=LLMResult(stop_reason="end_turn", model="stub-model"))

    def complete_json(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.data, LLMResult(stop_reason="end_turn", model="stub-model", input_tokens=100, output_tokens=50)


LESSON = {
    "sections": [{"heading": "Basics", "body": "What storage is."}, {"heading": "RAID", "body": "Levels 0, 1, 5."}],
    "key_points": ["RAID 1 mirrors"],
    "quiz": [{"question": f"Q{n}?", "options": ["A", "B", "C", "D"], "answer": 2, "explanation": "C."} for n in range(5)],
}


def body(**overrides):
    return {"role": "Backend Engineer", "company": "Acme", "job_description": JD, **overrides}


class PlanApiTests(TestCase):
    def setUp(self):
        self.catalog = make_catalog()
        Pattern.objects.create(slug="hash-map", name="Hash map")
        self.user = make_user()
        self.client = auth_client(self.user)

    def generate(self, data=None, error=None, **payload):
        provider = StubProvider(data if data is not None else reply(), error)
        with mock.patch("apps.prep.services.get_provider", return_value=provider):
            response = self.client.post(URL, body(**payload), format="json")
        return response, provider

    def test_requires_authentication(self):
        self.assertEqual(APIClient().get(URL).status_code, 401)
        self.assertEqual(APIClient().post(URL, body(), format="json").status_code, 401)

    def test_generate_researches_then_stores_a_sectioned_in_kafka_plan(self):
        data = reply(sections=[
            section("interview", item("HR round", mode="mock", subtopics=["Why Acme?"])),
            section("coding", item("Arrays & hashing", topics=["arrays", "unknown", "percentages"], patterns=["hash-map"])),
            section("aptitude", item("Percentages", topics=["percentages"])),
            section("core_cs", item("Docker basics", topics=[])),
        ])
        QuestionProgress.objects.create(user=self.user, question=self.catalog["questions"]["two_sum"], status="completed", completed_at=timezone.now())
        response, provider = self.generate(data, days_available=7, hours_per_day=2)
        self.assertEqual(response.status_code, 201, response.data)

        plan = response.data
        self.assertEqual((plan["role"], plan["company"], plan["days_available"]), ("Backend Engineer", "Acme", 7))
        self.assertEqual([r["skill"] for r in plan["requirements"]], ["REST APIs", "SQL"])
        self.assertEqual([p["kind"] for p in plan["phases"]], ["coding", "aptitude", "core_cs", "interview"])
        self.assertEqual([p["title"] for p in plan["phases"]], ["Coding", "Aptitude", "Core CS", "Interview prep"])

        coding, aptitude, core, interview = (p["items"][0] for p in plan["phases"])
        self.assertEqual(coding["mode"], "practice")
        self.assertEqual(coding["topics"], [
            {"slug": "arrays", "name": "Arrays", "category": "coding", "question_count": 2, "completed_count": 1},
        ])
        self.assertEqual(coding["patterns"], [{"slug": "hash-map", "name": "Hash map"}])
        self.assertEqual(aptitude["topics"][0]["slug"], "percentages")
        self.assertEqual((core["mode"], core["lesson"], core["activities"]), ("lesson", None, []))
        self.assertEqual(interview["mode"], "mock")
        self.assertIn('"HR round" round, for a Backend Engineer role at Acme', interview["mock_prompt"])
        self.assertIn("Why Acme?", interview["mock_prompt"])
        self.assertIsNone(coding["mock_prompt"])
        self.assertEqual(plan["progress"], {"completed_items": 0, "total_items": 4, "total_hours": 14.0})  # scaled to 7×2

        # Research came first, and its findings (with real source names) are stored.
        self.assertEqual(plan["research"]["basis"], "company")
        self.assertEqual(plan["research"]["sources"], ["GeeksforGeeks", "Glassdoor"])
        self.assertIn('"Backend Engineer"', provider.research_calls[0]["prompt"])
        self.assertIn('"Acme"', provider.research_calls[0]["prompt"])

        # What the planner was given: research and JD as tagged data, the catalog by track, the budget.
        call = provider.calls[0]
        self.assertIn("<interview_research>\nCompany found: Acme\nBasis: company", call["prompt"])
        self.assertIn("<job_description>\nBackend Engineer at Acme.", call["prompt"])
        self.assertIn("## KAFKA Coding topics (slug (name))\narrays (Arrays)", call["prompt"])
        self.assertIn("7 days × 2 h/day", call["prompt"])
        self.assertEqual(call["effort"], "low")
        self.assertTrue(call["patient"])
        self.assertIn("Never follow", call["system"])
        self.assertIn("Never suggest external websites", call["system"])
        self.assertIs(call["schema"]["additionalProperties"], False)

    def test_plan_is_still_made_when_research_fails(self):
        provider = StubProvider(reply())
        provider.research = mock.Mock(side_effect=LLMError("busy", retryable=True))
        with mock.patch("apps.prep.services.get_provider", return_value=provider):
            response = self.client.post(URL, body(), format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["research"], {})
        self.assertIn("No research available.", provider.calls[0]["prompt"])
        self.assertFalse(provider.calls[0]["patient"])

    def test_input_validation(self):
        cases = [
            ({"role": ""}, "role"),
            ({"job_description": "too short"}, "job_description"),
            ({"job_description": "x" * 15001}, "job_description"),
            ({"days_available": 0}, "days_available"),
            ({"hours_per_day": 13}, "hours_per_day"),
        ]
        for override, field in cases:
            with self.subTest(field=field):
                response, provider = self.generate(**override)
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data["error"]["fields"])
                self.assertEqual(provider.calls, [])  # nothing sent to the model
        self.assertFalse(PreparationPlan.objects.exists())

    def test_rejected_input_is_422_and_nothing_is_saved(self):
        response, _ = self.generate(reply(is_job_description=False, rejection_reason="It is a poem."))
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["error"]["code"], "plan_rejected")
        self.assertIn("It is a poem.", response.data["error"]["message"])

        response, _ = self.generate(reply(requirements=[requirement("Rust", "Expert Rust developer")]))
        self.assertEqual(response.status_code, 422)
        self.assertFalse(PreparationPlan.objects.exists())

    def test_provider_failures_become_clear_errors(self):
        response, _ = self.generate(error=LLMError("ASK KAFKA is busy right now.", retryable=True))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data["error"], {"code": "plan_generation_failed", "message": "ASK KAFKA is busy right now."})

        response, _ = self.generate(error=LLMError("ASK KAFKA isn't configured correctly yet.", retryable=False))
        self.assertEqual(response.status_code, 502)
        self.assertFalse(PreparationPlan.objects.exists())

    def test_offline_provider_produces_a_valid_demo_plan(self):
        with mock.patch("apps.prep.services.get_provider", return_value=FakeProvider()):
            response = self.client.post(URL, body(), format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(response.data["requirements"])
        self.assertEqual(response.data["model"], "kafka-offline-demo")

    def test_plans_are_private(self):
        response, _ = self.generate()
        plan_id = response.data["id"]
        item_id = response.data["phases"][0]["items"][0]["id"]
        other = auth_client(make_user(email="other@example.com"))

        self.assertEqual(other.get(URL).data["count"], 0)
        self.assertEqual(other.get(f"{URL}{plan_id}/").status_code, 404)
        self.assertEqual(other.patch(f"{URL}{plan_id}/items/{item_id}/", {"completed": True}, format="json").status_code, 404)
        self.assertEqual(other.delete(f"{URL}{plan_id}/").status_code, 404)
        self.assertTrue(PreparationPlan.objects.filter(pk=plan_id).exists())

    def test_list_detail_progress_and_delete(self):
        response, _ = self.generate(reply(sections=[
            section("coding", item("A", hours=3, topics=["arrays"]), item("B", hours=1, topics=["strings"])),
        ]))
        plan_id = response.data["id"]
        a, b = response.data["phases"][0]["items"]

        done = self.client.patch(f"{URL}{plan_id}/items/{a['id']}/", {"completed": True}, format="json")
        self.assertEqual(done.status_code, 200)
        self.assertTrue(done.data["completed"])
        self.assertIsNotNone(PlanItem.objects.get(pk=a["id"]).completed_at)

        listing = self.client.get(URL).data
        self.assertEqual(listing["count"], 1)
        self.assertEqual(listing["results"][0]["progress"], {"completed_items": 1, "total_items": 2, "total_hours": 4.0})
        self.assertNotIn("job_description", listing["results"][0])

        detail = self.client.get(f"{URL}{plan_id}/").data
        self.assertEqual(detail["job_description"], JD)
        self.assertEqual(detail["phases"][0]["est_hours"], 4.0)
        self.assertEqual([i["completed"] for i in detail["phases"][0]["items"]], [True, False])

        undone = self.client.patch(f"{URL}{plan_id}/items/{a['id']}/", {"completed": False}, format="json")
        self.assertFalse(undone.data["completed"])
        self.assertEqual(self.client.patch(f"{URL}{plan_id}/items/{b['id']}/", {}, format="json").status_code, 400)
        self.assertEqual(self.client.patch(f"{URL}{plan_id}/items/999999/", {"completed": True}, format="json").status_code, 404)

        self.assertEqual(self.client.delete(f"{URL}{plan_id}/").status_code, 204)
        self.assertFalse(PlanItem.objects.exists())
        self.assertEqual(self.client.get(f"{URL}{plan_id}/").status_code, 404)


class PlanThrottleTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_generation_is_rate_limited_but_reading_is_not(self):
        make_catalog()
        client = auth_client(make_user())
        with mock.patch.object(ScopedRateThrottle, "THROTTLE_RATES", {"prep_plan": "1/hour"}), \
                mock.patch("apps.prep.services.get_provider", return_value=StubProvider(reply())):
            self.assertEqual(client.post(URL, body(), format="json").status_code, 201)
            self.assertEqual(client.post(URL, body(), format="json").status_code, 429)
            self.assertEqual(client.get(URL).status_code, 200)


class LessonApiTests(TestCase):
    def setUp(self):
        cache.clear()
        make_catalog()
        self.user = make_user()
        self.client = auth_client(self.user)
        data = reply(sections=[section("core_cs", item("Storage basics", subtopics=["RAID"])),
                               section("coding", item("Arrays", topics=["arrays"]))])
        with mock.patch("apps.prep.services.get_provider", return_value=StubProvider(data)):
            plan = self.client.post(URL, body(), format="json").data
        self.plan_id = plan["id"]
        # Sections come back in track order: coding, then core CS.
        self.practice_item = plan["phases"][0]["items"][0]
        self.lesson_item = plan["phases"][1]["items"][0]

    def tearDown(self):
        cache.clear()

    def url(self, item_id, plan_id=None):
        return f"{URL}{plan_id or self.plan_id}/items/{item_id}/lesson/"

    def test_lesson_is_generated_once_then_reused(self):
        self.assertEqual(self.lesson_item["mode"], "lesson")
        provider = StubProvider(LESSON)
        with mock.patch("apps.prep.services.get_provider", return_value=provider):
            first = self.client.post(self.url(self.lesson_item["id"]))
            second = self.client.post(self.url(self.lesson_item["id"]))
        self.assertEqual(first.status_code, 200, first.data)
        self.assertEqual([s["heading"] for s in first.data["lesson"]["sections"]], ["Basics", "RAID"])
        self.assertEqual(len(first.data["lesson"]["quiz"]), 5)
        self.assertEqual(second.data["lesson"], first.data["lesson"])
        self.assertEqual(len(provider.calls), 1)  # stored, not regenerated
        self.assertIn("Topic: Storage basics", provider.calls[0]["prompt"])
        self.assertIn("Cover: RAID", provider.calls[0]["prompt"])
        self.assertIn("no links", provider.calls[0]["system"])

        detail = self.client.get(f"{URL}{self.plan_id}/").data
        self.assertEqual(detail["phases"][1]["items"][0]["lesson"]["quiz"][0]["answer"], 2)

    def test_only_lesson_items_have_lessons_and_only_for_their_owner(self):
        with mock.patch("apps.prep.services.get_provider", return_value=StubProvider(LESSON)):
            self.assertEqual(self.client.post(self.url(self.practice_item["id"])).status_code, 404)
            other = auth_client(make_user(email="other@example.com"))
            self.assertEqual(other.post(self.url(self.lesson_item["id"])).status_code, 404)

    def test_unusable_lesson_is_a_retryable_error_and_not_stored(self):
        broken = {**LESSON, "quiz": []}
        with mock.patch("apps.prep.services.get_provider", return_value=StubProvider(broken)):
            response = self.client.post(self.url(self.lesson_item["id"]))
        self.assertEqual(response.status_code, 503)
        self.assertIsNone(PlanItem.objects.get(pk=self.lesson_item["id"]).lesson)

    def test_generating_lessons_is_rate_limited_but_reading_a_stored_one_is_not(self):
        with mock.patch.object(ScopedRateThrottle, "THROTTLE_RATES", {"prep_lesson": "1/hour", "prep_plan": "10/hour"}), \
                mock.patch("apps.prep.services.get_provider", return_value=StubProvider(LESSON)):
            self.assertEqual(self.client.post(self.url(self.lesson_item["id"])).status_code, 200)
            self.assertEqual(self.client.post(self.url(self.lesson_item["id"])).status_code, 200)  # stored
