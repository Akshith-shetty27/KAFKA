from datetime import datetime, timedelta
from datetime import timezone as dt_timezone
from unittest import mock

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from apps.core.testing import auth_client, make_catalog, make_user
from apps.progress import services
from apps.progress.models import ActivityEvent, QuestionProgress


class ProgressWriteTests(APITestCase):
    def setUp(self):
        self.data = make_catalog()
        self.q = self.data["questions"]
        self.opt = self.data["options"]
        self.user = make_user()
        self.client = auth_client(self.user)

    def test_write_endpoints_require_login(self):
        anon = APIClient()
        self.assertEqual(anon.post(reverse("question-attempt", args=["two-sum"])).status_code, 401)
        self.assertEqual(anon.post(reverse("question-answer", args=["pct-q"]), {"option_id": 1}).status_code, 401)
        self.assertEqual(anon.put(reverse("question-progress", args=["two-sum"]), {"status": "completed"}).status_code, 401)

    def test_attempt_is_idempotent_and_logged_once_per_day(self):
        url = reverse("question-attempt", args=["two-sum"])
        self.assertEqual(self.client.post(url).json()["status"], "attempted")
        self.client.post(url)
        self.assertEqual(QuestionProgress.objects.filter(user=self.user).count(), 1)
        self.assertEqual(ActivityEvent.objects.filter(user=self.user, event_type="attempted").count(), 1)

    def test_wrong_then_right_answer(self):
        url = reverse("question-answer", args=["pct-q"])
        wrong = self.client.post(url, {"option_id": self.opt["A"].id}, format="json").json()
        self.assertFalse(wrong["is_correct"])
        self.assertEqual(wrong["correct_option_id"], self.opt["B"].id)
        self.assertEqual(wrong["progress"]["status"], "attempted")
        self.assertFalse(wrong["progress"]["first_attempt_correct"])

        right = self.client.post(url, {"option_id": self.opt["B"].id}, format="json").json()
        self.assertTrue(right["is_correct"])
        self.assertEqual(right["progress"]["status"], "completed")
        self.assertEqual(right["progress"]["answer_count"], 2)
        self.assertFalse(right["progress"]["first_attempt_correct"])  # history can't be rewritten

        events = ActivityEvent.objects.filter(user=self.user)
        self.assertEqual(events.filter(event_type="answered").count(), 2)
        self.assertEqual(events.filter(event_type="completed").count(), 1)

    def test_answer_with_option_from_another_question_is_rejected(self):
        response = self.client.post(
            reverse("question-answer", args=["pct-q"]), {"option_id": 999999}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("option_id", response.json()["error"]["fields"])

    def test_answering_a_coding_question_is_rejected(self):
        response = self.client.post(
            reverse("question-answer", args=["two-sum"]), {"option_id": self.opt["A"].id}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_mark_complete_and_reset(self):
        url = reverse("question-progress", args=["two-sum"])
        body = self.client.put(url, {"status": "completed"}, format="json").json()
        self.assertEqual(body["status"], "completed")
        self.assertIsNotNone(body["completed_at"])
        self.client.put(url, {"status": "completed"}, format="json")  # idempotent
        self.assertEqual(ActivityEvent.objects.filter(event_type="completed").count(), 1)

        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertFalse(QuestionProgress.objects.filter(user=self.user).exists())
        self.assertEqual(ActivityEvent.objects.filter(user=self.user).count(), 1)  # history kept

    def test_mcq_cannot_be_marked_complete_manually(self):
        response = self.client.put(reverse("question-progress", args=["pct-q"]), {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_unpublished_question_is_404_for_writes(self):
        self.assertEqual(self.client.post(reverse("question-attempt", args=["draft-q"])).status_code, 404)

    def test_reset_only_touches_my_own_record(self):
        other = make_user("other@example.com")
        services.mark_completed(other, self.q["two_sum"])
        self.client.delete(reverse("question-progress", args=["two-sum"]))
        self.assertTrue(QuestionProgress.objects.filter(user=other, question=self.q["two_sum"]).exists())


class StatsTests(APITestCase):
    def setUp(self):
        self.data = make_catalog()
        self.q = self.data["questions"]
        self.opt = self.data["options"]
        self.user = make_user()
        self.client = auth_client(self.user)

    def test_summary(self):
        services.mark_completed(self.user, self.q["two_sum"])
        services.record_attempt(self.user, self.q["anagram"])
        services.submit_answer(self.user, self.q["pct"], self.opt["A"].id)
        services.submit_answer(self.user, self.q["pct"], self.opt["B"].id)

        body = self.client.get(reverse("progress-summary")).json()
        self.assertEqual(body["totals"], {"questions": 4, "attempted": 3, "completed": 2, "completion_rate": 0.5})
        self.assertEqual(body["answers"], {"total": 2, "correct": 1, "incorrect": 1, "accuracy": 0.5})
        self.assertEqual(body["streak"]["current"], 1)
        self.assertTrue(body["streak"]["active_today"])
        aptitude = next(c for c in body["categories"] if c["slug"] == "aptitude")
        self.assertEqual((aptitude["answers_total"], aptitude["answers_correct"]), (2, 1))

    def test_summary_for_new_user_is_all_zero(self):
        body = self.client.get(reverse("progress-summary")).json()
        self.assertEqual(body["totals"]["attempted"], 0)
        self.assertIsNone(body["answers"]["accuracy"])
        self.assertEqual(body["streak"], {"current": 0, "longest": 0, "active_today": False})

    def test_streak_uses_the_users_timezone(self):
        # 20:00 UTC on Nov 12 is already Nov 13 in India (UTC+5:30).
        self.user.profile.timezone = "Asia/Kolkata"
        self.user.profile.save()
        utc_evening = datetime(2026, 11, 12, 20, 0, tzinfo=dt_timezone.utc)
        ActivityEvent.objects.create(
            user=self.user, event_type="attempted", question=self.q["anagram"], created_at=utc_evening
        )
        with mock.patch("django.utils.timezone.now", return_value=utc_evening + timedelta(hours=1)):
            activity = self.client.get(reverse("progress-activity"), {"days": 7}).json()["series"]
            summary = self.client.get(reverse("progress-summary")).json()
        self.assertEqual(activity[-1]["date"], "2026-11-13")
        self.assertEqual(activity[-1]["questions"], 1)  # counted on the *local* day
        self.assertEqual(activity[-2]["questions"], 0)
        self.assertTrue(summary["streak"]["active_today"])

    def test_activity_series(self):
        services.mark_completed(self.user, self.q["two_sum"])
        old = ActivityEvent.objects.create(user=self.user, event_type="attempted", question=self.q["anagram"])
        old.created_at = timezone.now() - timedelta(days=2)
        old.save()

        body = self.client.get(reverse("progress-activity"), {"days": 7}).json()
        series = body["series"]
        self.assertEqual(len(series), 7)
        self.assertEqual(series[-1]["completed"], 1)
        self.assertEqual(series[-1]["questions"], 1)
        self.assertEqual(series[-3]["questions"], 1)
        self.assertEqual(sum(day["questions"] for day in series), 2)

    def test_activity_rejects_unsupported_range(self):
        self.assertEqual(self.client.get(reverse("progress-activity"), {"days": 3}).status_code, 400)

    def test_recent_lists_only_my_questions_newest_first(self):
        other = make_user("other@example.com")
        services.record_attempt(other, self.q["max_sub"])
        services.record_attempt(self.user, self.q["two_sum"])
        services.record_attempt(self.user, self.q["anagram"])

        body = self.client.get(reverse("progress-recent")).json()
        self.assertEqual([r["question"]["slug"] for r in body], ["anagram", "two-sum"])
        self.assertEqual(body[0]["status"], "attempted")
        self.assertEqual(body[0]["question"]["status"], "attempted")

    def test_plan_spreads_goal_and_marks_done_items(self):
        self.user.profile.daily_goal = 3
        self.user.profile.save()
        services.mark_completed(self.user, self.q["two_sum"])

        body = self.client.get(reverse("progress-plan")).json()
        self.assertEqual(body["daily_goal"], 3)
        items = [(i["question"]["slug"], i["done"]) for i in body["items"]]
        # 2 categories → coding gets 2 slots, aptitude 1. two-sum (done today) fills a coding slot.
        self.assertEqual(items, [("two-sum", True), ("max-subarray", False), ("pct-q", False)])
        self.assertEqual(body["completed_today"], 1)
        self.assertEqual([t["slug"] for t in body["recommended_topics"]], ["arrays", "percentages"])

    def test_stats_endpoints_require_login(self):
        for name in ["progress-summary", "progress-activity", "progress-recent", "progress-plan"]:
            self.assertEqual(APIClient().get(reverse(name)).status_code, 401, name)
