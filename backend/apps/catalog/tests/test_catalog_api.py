from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from apps.core.testing import auth_client, make_catalog, make_user
from apps.progress import services


class CatalogAuthTests(APITestCase):
    def test_catalog_requires_login(self):
        for name in ["category-list", "topic-list", "question-list", "pattern-list"]:
            self.assertEqual(APIClient().get(reverse(name)).status_code, 401, name)


class CatalogApiTests(APITestCase):
    def setUp(self):
        self.data = make_catalog()
        self.q = self.data["questions"]
        self.user = make_user()
        self.client = auth_client(self.user)

    def test_categories_count_only_published_questions_and_my_progress(self):
        services.mark_completed(self.user, self.q["two_sum"])
        services.record_attempt(self.user, self.q["anagram"])
        body = {c["slug"]: c for c in self.client.get(reverse("category-list")).json()}
        self.assertEqual(body["coding"]["question_count"], 3)
        self.assertEqual(body["coding"]["attempted_count"], 2)
        self.assertEqual(body["coding"]["completed_count"], 1)
        self.assertEqual(body["aptitude"]["question_count"], 1)  # draft excluded

    def test_topics_filtered_by_category(self):
        body = self.client.get(reverse("topic-list"), {"category": "coding"}).json()
        self.assertEqual([t["slug"] for t in body], ["arrays", "strings"])
        self.assertEqual(body[0]["question_count"], 2)

    def test_question_list_is_paginated_and_hides_drafts(self):
        body = self.client.get(reverse("question-list")).json()
        self.assertEqual(body["count"], 4)
        self.assertNotIn("draft-q", [q["slug"] for q in body["results"]])
        self.assertEqual(set(body), {"count", "next", "previous", "results"})

    def test_question_list_filters(self):
        url = reverse("question-list")
        slugs = lambda params: [q["slug"] for q in self.client.get(url, params).json()["results"]]  # noqa: E731
        self.assertEqual(slugs({"category": "coding", "difficulty": "medium"}), ["max-subarray"])
        self.assertEqual(slugs({"topic": "strings"}), ["anagram"])
        self.assertEqual(slugs({"search": "two"}), ["two-sum"])

        services.mark_completed(self.user, self.q["two_sum"])
        self.assertEqual(slugs({"status": "completed"}), ["two-sum"])
        self.assertNotIn("two-sum", slugs({"status": "not_started"}))

    def test_invalid_filter_is_400(self):
        response = self.client.get(reverse("question-list"), {"difficulty": "impossible"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("difficulty", response.json()["error"]["fields"])

    def test_coding_detail_includes_solutions_preferred_language_first(self):
        self.user.profile.preferred_language = "java"
        self.user.profile.save()
        body = self.client.get(reverse("question-detail", args=["two-sum"])).json()
        self.assertEqual(body["coding"]["approach"], "Hash it.")
        self.assertEqual([s["language"] for s in body["solutions"]], ["java", "python"])
        self.assertEqual(body["navigation"], {"previous": None, "next": "max-subarray"})
        self.assertIsNone(body["progress"])

    def test_mcq_answer_is_hidden_until_answered(self):
        url = reverse("question-detail", args=["pct-q"])
        body = self.client.get(url).json()
        self.assertIsNone(body["answer"])
        self.assertIsNone(body["explanation"])
        self.assertTrue(all(set(o) == {"id", "label", "text"} for o in body["options"]))

        services.submit_answer(self.user, self.q["pct"], self.data["options"]["A"].id)
        body = self.client.get(url).json()
        self.assertEqual(body["answer"]["correct_option_id"], self.data["options"]["B"].id)
        self.assertEqual(body["explanation"], "100 → 120 → 96.")
        self.assertEqual(body["progress"]["selected_option_id"], self.data["options"]["A"].id)

    def test_unpublished_question_is_404(self):
        response = self.client.get(reverse("question-detail", args=["draft-q"]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")

    def test_another_users_progress_never_leaks_into_my_views(self):
        other = make_user("other@example.com")
        services.mark_completed(other, self.q["two_sum"])
        services.submit_answer(other, self.q["pct"], self.data["options"]["B"].id)

        cats = {c["slug"]: c for c in self.client.get(reverse("category-list")).json()}
        self.assertEqual(cats["coding"]["completed_count"], 0)
        listing = self.client.get(reverse("question-list")).json()["results"]
        self.assertTrue(all(q["status"] is None for q in listing))
        detail = self.client.get(reverse("question-detail", args=["pct-q"])).json()
        self.assertIsNone(detail["progress"])
        self.assertIsNone(detail["answer"])  # other user's answer doesn't unlock mine
