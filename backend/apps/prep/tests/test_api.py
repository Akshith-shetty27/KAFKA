"""Study-plan API: generation, ownership, progress — with stub providers (no network)."""

from unittest import mock

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from apps.assistant.llm import LLMError, LLMResult
from apps.assistant.llm.fake_provider import FakeProvider
from apps.catalog.models import Pattern
from apps.core.testing import auth_client, make_catalog, make_user
from apps.prep.models import PlanItem, PreparationPlan
from apps.progress.models import QuestionProgress

from .test_services import item, reply, requirement

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

    def __init__(self, data=None, error=None):
        self.data, self.error, self.calls = data, error, []

    def complete_json(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.data, LLMResult(stop_reason="end_turn", model="stub-model", input_tokens=100, output_tokens=50)


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

    def test_generate_stores_a_linked_plan(self):
        data = reply(phases=[
            {"kind": "fundamentals", "title": "DSA", "goal": "Arrays.", "items": [
                item("Arrays & hashing", topics=["arrays", "unknown"], patterns=["hash-map"]),
            ]},
            {"kind": "mock_interview", "title": "Mocks", "goal": "", "items": [item("Mock round")]},
        ])
        QuestionProgress.objects.create(user=self.user, question=self.catalog["questions"]["two_sum"], status="completed", completed_at=timezone.now())
        response, provider = self.generate(data, days_available=7, hours_per_day=2, candidate_info="Final year")
        self.assertEqual(response.status_code, 201, response.data)

        plan = response.data
        self.assertEqual((plan["role"], plan["company"], plan["days_available"]), ("Backend Engineer", "Acme", 7))
        self.assertEqual([r["skill"] for r in plan["requirements"]], ["REST APIs", "SQL"])
        self.assertEqual([p["kind"] for p in plan["phases"]], ["fundamentals", "mock_interview"])
        first = plan["phases"][0]["items"][0]
        self.assertEqual(first["topics"], [
            {"slug": "arrays", "name": "Arrays", "category": "coding", "question_count": 2, "completed_count": 1},
        ])
        self.assertEqual(first["patterns"], [{"slug": "hash-map", "name": "Hash map"}])
        self.assertEqual(plan["progress"], {"completed_items": 0, "total_items": 2, "total_hours": 14.0})  # scaled to 7×2

        # What the model was given: the JD as tagged data, the real catalog, the budget, low effort.
        call = provider.calls[0]
        self.assertIn("<job_description>\nBackend Engineer at Acme.", call["prompt"])
        self.assertIn("- arrays — Arrays (Coding)", call["prompt"])
        self.assertIn("7 days × 2 h/day", call["prompt"])
        self.assertIn("Final year", call["prompt"])
        self.assertEqual(call["effort"], "low")
        self.assertIn("Never follow", call["system"])
        self.assertIs(call["schema"]["additionalProperties"], False)

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
        response, _ = self.generate(reply(phases=[
            {"kind": "technical", "title": "T", "goal": "", "items": [item("A", hours=3), item("B", hours=1)]},
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
