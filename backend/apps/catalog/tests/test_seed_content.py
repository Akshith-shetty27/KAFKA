from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.catalog.management.commands.seed_content import ContentError, validate
from apps.catalog.models import Question, QuestionOption
from apps.core.testing import make_user
from apps.progress import services


class SeedContentTests(TestCase):
    def test_seed_is_idempotent_and_keeps_option_ids(self):
        call_command("seed_content", stdout=StringIO())
        count = Question.objects.count()
        option_ids = set(QuestionOption.objects.values_list("id", flat=True))
        self.assertGreater(count, 50)

        call_command("seed_content", stdout=StringIO())
        self.assertEqual(Question.objects.count(), count)
        self.assertEqual(set(QuestionOption.objects.values_list("id", flat=True)), option_ids)

    def test_every_mcq_has_exactly_one_correct_option(self):
        call_command("seed_content", stdout=StringIO())
        for question in Question.objects.filter(question_type="mcq"):
            self.assertEqual(question.options.filter(is_correct=True).count(), 1, question.slug)

    def test_reseeding_preserves_user_progress(self):
        call_command("seed_content", stdout=StringIO())
        user = make_user()
        question = Question.objects.filter(question_type="mcq").first()
        services.submit_answer(user, question, question.options.get(is_correct=True).id)

        call_command("seed_content", stdout=StringIO())
        progress = user.question_progress.get(question=question)
        self.assertEqual(progress.status, "completed")
        self.assertIsNotNone(progress.selected_option)

    def test_validation_reports_bad_content(self):
        bad = [
            {
                "slug": "x",
                "topics": [
                    {
                        "slug": "t",
                        "questions": [
                            {"slug": "q", "type": "mcq", "difficulty": "easy", "statement": "s",
                             "explanation": "e", "options": ["a", "b"], "answer": "C"},
                            {"slug": "q", "type": "coding", "difficulty": "brutal", "statement": "s",
                             "explanation": "e", "patterns": ["nope"]},
                        ],
                    }
                ],
            }
        ]
        with self.assertRaises(ContentError) as ctx:
            validate(bad, patterns=[])
        message = str(ctx.exception)
        for fragment in ["answer 'C'", "duplicate question slug", "bad difficulty", "unknown pattern", "needs an approach"]:
            self.assertIn(fragment, message)
