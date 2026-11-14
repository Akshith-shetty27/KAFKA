from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.assistant import context, prompts
from apps.catalog.models import Solution
from apps.core.testing import make_catalog, make_user
from apps.progress import services as progress


class ContextRevealRulesTests(TestCase):
    """The anti-spoiler rule lives in what the model is given."""

    def setUp(self):
        self.data = make_catalog()
        self.q = self.data["questions"]
        self.opt = self.data["options"]
        self.user = make_user()
        Solution.objects.filter(question=self.q["two_sum"], language="python").update(code="SECRET_SOLUTION_CODE")

    def test_hint_on_unsolved_question_withholds_solution(self):
        text, revealed = context.build_question_context(self.user, self.q["two_sum"], "hint")
        self.assertFalse(revealed)
        self.assertIn("Find two numbers.", text)  # statement is there
        self.assertNotIn("SECRET_SOLUTION_CODE", text)
        self.assertNotIn("Hash it.", text)  # approach withheld
        self.assertNotIn("Use a hash map.", text)  # explanation withheld
        self.assertIn("deliberately withheld", text)

    def test_explain_includes_solution(self):
        text, revealed = context.build_question_context(self.user, self.q["two_sum"], "explain")
        self.assertTrue(revealed)
        self.assertIn("SECRET_SOLUTION_CODE", text)
        self.assertIn("Hash it.", text)

    def test_completed_question_reveals_even_in_chat(self):
        progress.mark_completed(self.user, self.q["two_sum"])
        text, revealed = context.build_question_context(self.user, self.q["two_sum"], "chat")
        self.assertTrue(revealed)
        self.assertIn("SECRET_SOLUTION_CODE", text)

    def test_unanswered_mcq_does_not_mark_correct_option(self):
        text, _ = context.build_question_context(self.user, self.q["pct"], "hint")
        self.assertIn("B. 4% decrease", text)
        self.assertNotIn("(correct)", text)

    def test_review_shows_correct_option_and_student_answer(self):
        progress.submit_answer(self.user, self.q["pct"], self.opt["A"].id)
        text, _ = context.build_question_context(self.user, self.q["pct"], "review")
        self.assertIn("B. 4% decrease (correct)", text)
        self.assertIn("Their latest answer: A. No change (incorrect)", text)

    def test_other_users_progress_is_not_used(self):
        other = make_user("other@example.com")
        progress.mark_completed(other, self.q["two_sum"])
        text, revealed = context.build_question_context(self.user, self.q["two_sum"], "chat")
        self.assertFalse(revealed)
        self.assertNotIn("SECRET_SOLUTION_CODE", text)


class CapabilityTests(TestCase):
    def setUp(self):
        self.data = make_catalog()
        self.q = self.data["questions"]
        self.user = make_user()

    def test_matrix(self):
        self.assertEqual(context.capabilities(self.user, None).as_dict(), {"hint": False, "explain": False, "review": False})
        self.assertEqual(context.capabilities(self.user, self.q["two_sum"]).as_dict(), {"hint": True, "explain": True, "review": False})
        self.assertEqual(context.capabilities(self.user, self.q["pct"]).as_dict(), {"hint": True, "explain": False, "review": False})
        progress.submit_answer(self.user, self.q["pct"], self.data["options"]["B"].id)
        self.assertEqual(context.capabilities(self.user, self.q["pct"]).as_dict(), {"hint": False, "explain": True, "review": True})

    def test_mode_checks(self):
        context.check_mode_allowed(self.user, None, "chat")
        with self.assertRaises(ValidationError):
            context.check_mode_allowed(self.user, None, "hint")
        with self.assertRaises(ValidationError):
            context.check_mode_allowed(self.user, self.q["pct"], "explain")  # answer first


class PromptTests(TestCase):
    def test_hint_prompt_has_level_and_mode(self):
        system = prompts.build_system_prompt(mode="hint", hint_level=2, question_context="## Current question", preferred_language="Java")
        self.assertIn("MODE: hint", system)
        self.assertIn("HINT LEVEL: 2", system)
        self.assertIn("preferred programming language is Java", system)
        # Stable instructions first (prompt-cache friendly), mode last.
        self.assertLess(system.index("You are ASK KAFKA"), system.index("## Current question"))
        self.assertLess(system.index("## Current question"), system.index("MODE: hint"))
