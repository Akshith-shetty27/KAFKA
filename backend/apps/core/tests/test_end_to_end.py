"""
One student's whole journey through the API, in order — the integration test
that catches the pieces not fitting together (cookie auth → catalog → grading
→ progress → stats → ASK KAFKA → sign-out). Uses the offline LLM provider.
"""

import json

from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from apps.core.testing import PASSWORD, make_catalog

COOKIE = settings.REFRESH_COOKIE_NAME


def sse_events(response):
    body = b"".join(response.streaming_content).decode()
    return [json.loads(line[6:]) for line in body.splitlines() if line.startswith("data: ")]


class StudentJourneyTests(APITestCase):
    def setUp(self):
        self.data = make_catalog()
        self.browser = APIClient()  # keeps cookies between requests, like a browser

    def bearer(self, access):
        self.browser.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_full_journey(self):
        b = self.browser

        # 1. Sign up → access token in JSON, refresh token only in the httpOnly cookie.
        r = b.post(reverse("auth-register"), {"email": "meera@example.com", "password": PASSWORD, "first_name": "Meera", "timezone": "Asia/Kolkata"}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertIn(COOKIE, r.cookies)

        # 2. "Page reload": the access token is gone, the cookie restores the session.
        b.credentials()
        self.assertEqual(b.get(reverse("auth-me")).status_code, 401)
        access = b.post(reverse("auth-refresh")).json()["access"]
        self.bearer(access)
        self.assertEqual(b.get(reverse("auth-me")).json()["profile"]["timezone"], "Asia/Kolkata")

        # 3. Browse the catalog.
        categories = {c["slug"]: c for c in b.get(reverse("category-list")).json()}
        self.assertEqual(categories["coding"]["completed_count"], 0)
        listing = b.get(reverse("question-list"), {"category": "aptitude"}).json()
        self.assertEqual([q["slug"] for q in listing["results"]], ["pct-q"])

        # 4. MCQ: the answer is hidden until graded on the server.
        detail = b.get(reverse("question-detail", args=["pct-q"])).json()
        self.assertIsNone(detail["answer"])
        wrong = next(o["id"] for o in detail["options"] if o["label"] == "A")
        right = next(o["id"] for o in detail["options"] if o["label"] == "B")
        graded = b.post(reverse("question-answer", args=["pct-q"]), {"option_id": wrong}, format="json").json()
        self.assertFalse(graded["is_correct"])
        self.assertEqual(graded["correct_option_id"], right)

        # 5. Coding: open it, then mark it solved.
        b.post(reverse("question-attempt", args=["two-sum"]))
        done = b.put(reverse("question-progress", args=["two-sum"]), {"status": "completed"}, format="json").json()
        self.assertEqual(done["status"], "completed")

        # 6. Stats reflect it everywhere.
        summary = b.get(reverse("progress-summary")).json()
        self.assertEqual((summary["totals"]["attempted"], summary["totals"]["completed"]), (2, 1))
        self.assertEqual(summary["answers"], {"total": 1, "correct": 0, "incorrect": 1, "accuracy": 0.0})
        self.assertEqual(summary["streak"]["current"], 1)
        plan = b.get(reverse("progress-plan")).json()
        self.assertIn(("two-sum", True), [(i["question"]["slug"], i["done"]) for i in plan["items"]])
        insights = b.get(reverse("progress-insights")).json()
        pct = next(t for t in insights["topics"] if t["slug"] == "percentages")
        self.assertEqual(pct["first_attempt_accuracy"], 0.0)
        self.assertEqual(b.get(reverse("progress-recent")).json()[0]["question"]["slug"], "two-sum")

        # 7. ASK KAFKA about the MCQ: review is unlocked because it was answered.
        conv = b.post(reverse("conversation-list"), {"question_slug": "pct-q"}, format="json").json()
        self.assertEqual(conv["capabilities"], {"hint": False, "explain": True, "review": True})
        r = b.post(
            reverse("conversation-messages", args=[conv["id"]]),
            {"content": "Where did I go wrong?", "mode": "review"},
            format="json",
            HTTP_ACCEPT="text/event-stream",
        )
        events = sse_events(r)
        self.assertEqual([events[0]["type"], events[-1]["type"]], ["start", "done"])
        history = b.get(reverse("conversation-detail", args=[conv["id"]])).json()["messages"]
        self.assertEqual([m["role"] for m in history], ["user", "assistant"])
        today = b.get(reverse("progress-activity"), {"days": 7}).json()["series"][-1]
        self.assertEqual(today["ai_messages"], 1)

        # 8. Sign out → the refresh cookie no longer works.
        self.assertEqual(b.post(reverse("auth-logout")).status_code, 204)
        b.credentials()
        self.assertEqual(b.post(reverse("auth-refresh")).status_code, 401)
