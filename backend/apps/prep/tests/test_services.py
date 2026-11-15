"""Study-plan validation and input cleaning — the parts that keep plans JD-specific and safe."""

from decimal import Decimal

from django.test import SimpleTestCase, override_settings

from apps.prep import services
from apps.prep.services import PlanRejected, clean_jd_text, evidence_in_jd, validate_plan

JD = """Backend Engineer
Design and implement RESTful APIs in Python and Django.
Write efficient SQL queries on PostgreSQL and understand indexing.
Strong fundamentals in data structures and algorithms.
Nice to have: Docker and AWS."""


def requirement(skill, evidence, importance="high", category="dsa"):
    return {"skill": skill, "category": category, "importance": importance, "evidence": evidence}


def item(title="Item", hours=2, topics=(), patterns=(), **extra):
    return {
        "title": title, "category": "dsa", "importance": "high", "reason": "Because the JD says so.",
        "subtopics": ["a", "b"], "activities": ["Do x"], "est_hours": hours,
        "topics": list(topics), "patterns": list(patterns), **extra,
    }


def reply(**overrides):
    data = {
        "is_job_description": True,
        "rejection_reason": "",
        "summary": "Backend role.",
        "requirements": [
            requirement("REST APIs", "Design and implement RESTful APIs in Python and Django"),
            requirement("SQL", "efficient SQL queries on PostgreSQL", category="databases"),
        ],
        "phases": [{"kind": "fundamentals", "title": "Basics", "goal": "Know DSA.", "items": [item()]}],
    }
    data.update(overrides)
    return data


def validate(data, **kwargs):
    return validate_plan(data, jd_text=JD, topic_slugs={"arrays", "sql"}, pattern_slugs={"hash-map"}, **kwargs)


class CleanTextTests(SimpleTestCase):
    def test_normalises_whitespace_and_control_characters(self):
        text, truncated = clean_jd_text("Role\r\n\r\n\r\n\r\nPython\x00  \t\nSQL   ")
        self.assertEqual(text, "Role\n\nPython\nSQL")
        self.assertFalse(truncated)

    @override_settings(PREP_JD_PROMPT_CHARS=50)
    def test_long_text_is_trimmed_at_a_line_break(self):
        text, truncated = clean_jd_text("line one is here\n" * 10)
        self.assertTrue(truncated)
        self.assertLessEqual(len(text), 50)
        self.assertTrue(text.endswith("here"))


class EvidenceTests(SimpleTestCase):
    def setUp(self):
        self.norm = services._norm(JD)
        self.words = set(self.norm.split())

    def test_exact_quote_after_normalising_case_and_punctuation(self):
        self.assertTrue(evidence_in_jd("efficient SQL queries on PostgreSQL!", self.norm, self.words))

    def test_lightly_paraphrased_quote_still_counts(self):
        self.assertTrue(evidence_in_jd("implement RESTful APIs using Python", self.norm, self.words))

    def test_invented_evidence_is_rejected(self):
        self.assertFalse(evidence_in_jd("Experience with Kubernetes and Terraform", self.norm, self.words))
        self.assertFalse(evidence_in_jd("", self.norm, self.words))


class ValidatePlanTests(SimpleTestCase):
    def test_requirements_without_real_evidence_are_dropped(self):
        data = reply(requirements=reply()["requirements"] + [requirement("Kubernetes", "Deep Kubernetes expertise")])
        skills = [r["skill"] for r in validate(data)["requirements"]]
        self.assertEqual(skills, ["REST APIs", "SQL"])

    def test_plan_with_too_few_evidenced_requirements_is_rejected(self):
        data = reply(requirements=[requirement("Kubernetes", "Deep Kubernetes expertise")])
        with self.assertRaisesMessage(PlanRejected, "couldn't find clear requirements"):
            validate(data)

    def test_non_job_description_is_rejected_with_reason(self):
        with self.assertRaisesMessage(PlanRejected, "doesn't look like a job description. It is a recipe."):
            validate(reply(is_job_description=False, rejection_reason="It is a recipe."))

    def test_unknown_catalog_links_are_dropped(self):
        data = reply(phases=[{"kind": "technical", "title": "T", "goal": "", "items": [
            item(topics=["arrays", "made-up", "ARRAYS"], patterns=["hash-map", "nope"]),
        ]}])
        clean = validate(data)["phases"][0]["items"][0]
        self.assertEqual(clean["topics"], ["arrays"])
        self.assertEqual(clean["patterns"], ["hash-map"])

    def test_phases_follow_preparation_order_and_empty_phases_are_dropped(self):
        data = reply(phases=[
            {"kind": "mock_interview", "title": "Mocks", "goal": "", "items": [item()]},
            {"kind": "fundamentals", "title": "Basics", "goal": "", "items": [item()]},
            {"kind": "advanced", "title": "Empty", "goal": "", "items": []},
        ])
        self.assertEqual([p["kind"] for p in validate(data)["phases"]], ["fundamentals", "mock_interview"])

    def test_values_are_normalised_or_defaulted(self):
        data = reply(phases=[{"kind": "Mock Interview", "title": "", "goal": "", "items": [
            item(category="System Design", importance="URGENT", hours=999),
            item(hours="abc"),
        ]}])
        phase = validate(data)["phases"][0]
        self.assertEqual(phase["kind"], "mock_interview")
        self.assertEqual(phase["title"], "Mock interviews")
        first, second = phase["items"]
        self.assertEqual((first["category"], first["importance"], first["est_hours"]), ("system_design", "medium", Decimal("40")))
        self.assertEqual(second["est_hours"], Decimal("2"))

    def test_sizes_are_capped(self):
        data = reply(phases=[{"kind": "technical", "title": "T", "goal": "", "items": [item(f"I{n}") for n in range(10)]}])
        self.assertEqual(len(validate(data)["phases"][0]["items"]), services.MAX_ITEMS_PER_PHASE)

    def test_hours_are_scaled_to_the_students_budget(self):
        data = reply(phases=[{"kind": "technical", "title": "T", "goal": "", "items": [item(hours=10), item(hours=30)]}])
        items = validate(data, hours_budget=20)["phases"][0]["items"]
        self.assertEqual([i["est_hours"] for i in items], [Decimal("5"), Decimal("15")])

    def test_requirements_sorted_by_importance(self):
        data = reply(requirements=[
            requirement("SQL", "efficient SQL queries on PostgreSQL", importance="low"),
            requirement("REST APIs", "Design and implement RESTful APIs in Python and Django", importance="high"),
        ])
        self.assertEqual([r["skill"] for r in validate(data)["requirements"]], ["REST APIs", "SQL"])
