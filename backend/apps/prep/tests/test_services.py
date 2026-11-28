"""Study-plan validation, research and lessons — the parts that keep plans JD-specific, in-KAFKA and safe."""

from decimal import Decimal
from types import SimpleNamespace

from django.test import SimpleTestCase, override_settings

from apps.assistant.llm import LLMError, LLMResult, ResearchResult
from apps.assistant.llm.groq_provider import clean_research_text, site_name, sources_from
from apps.prep import services
from apps.prep.services import PlanRejected, clean_jd_text, evidence_in_jd, validate_lesson, validate_plan

JD = """Backend Engineer
Design and implement RESTful APIs in Python and Django.
Write efficient SQL queries on PostgreSQL and understand indexing.
Strong fundamentals in data structures and algorithms.
Nice to have: Docker and AWS."""

TRACKS = {"arrays": "coding", "strings": "coding", "percentages": "aptitude", "sql": "core-cs"}


def requirement(skill, evidence, importance="high", category="dsa"):
    return {"skill": skill, "category": category, "importance": importance, "evidence": evidence}


def item(title="Item", hours=2, topics=(), patterns=(), mode="practice", **extra):
    return {
        "title": title, "mode": mode, "category": "dsa", "importance": "high", "reason": "Because the JD says so.",
        "subtopics": ["a", "b"], "est_hours": hours, "topics": list(topics), "patterns": list(patterns), **extra,
    }


def section(kind, *items, goal="Goal."):
    return {"kind": kind, "goal": goal, "items": list(items)}


def research(**overrides):
    data = {
        "company_found": "Acme", "basis": "company", "summary": "Acme runs an OA then two technical rounds.",
        "rounds": [{"name": "Online assessment", "details": "Aptitude and two coding questions."}],
        "frequently_asked": ["Arrays", "SQL joins"],
    }
    data.update(overrides)
    return data


def reply(**overrides):
    data = {
        "is_job_description": True,
        "rejection_reason": "",
        "summary": "Backend role.",
        "research": research(),
        "requirements": [
            requirement("REST APIs", "Design and implement RESTful APIs in Python and Django"),
            requirement("SQL", "efficient SQL queries on PostgreSQL", category="databases"),
        ],
        "sections": [section("coding", item("Arrays", topics=["arrays"]))],
    }
    data.update(overrides)
    return data


def validate(data, **kwargs):
    kwargs.setdefault("sources", ["GeeksforGeeks"])
    return validate_plan(data, jd_text=JD, topic_tracks=TRACKS, pattern_slugs={"hash-map"}, **kwargs)


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

    def test_sections_follow_track_order_merge_repeats_and_drop_unknown_or_empty(self):
        data = reply(sections=[
            section("interview", item("HR round", mode="mock")),
            section("coding", item("Arrays", topics=["arrays"])),
            section("Core CS", item("SQL", topics=["sql"])),
            section("coding", item("Strings", topics=["strings"])),
            section("fundamentals", item("Old-style phase")),
            section("aptitude"),
        ])
        phases = validate(data)["phases"]
        self.assertEqual([p["kind"] for p in phases], ["coding", "core_cs", "interview"])
        self.assertEqual([p["title"] for p in phases], ["Coding", "Core CS", "Interview prep"])
        self.assertEqual([i["title"] for i in phases[0]["items"]], ["Arrays", "Strings"])

    def test_links_must_be_real_and_from_the_sections_own_track(self):
        data = reply(sections=[section("coding", item(
            topics=["arrays", "made-up", "ARRAYS", "percentages", "sql"], patterns=["hash-map", "nope"],
        ))])
        clean = validate(data)["phases"][0]["items"][0]
        self.assertEqual((clean["topics"], clean["patterns"], clean["mode"]), (["arrays"], ["hash-map"], "practice"))

    def test_patterns_only_count_in_the_coding_section(self):
        data = reply(sections=[section("core_cs", item(topics=["sql"], patterns=["hash-map"]))])
        self.assertEqual(validate(data)["phases"][0]["items"][0]["patterns"], [])

    def test_items_without_kafka_content_become_lessons_never_external_activities(self):
        data = reply(sections=[section(
            "core_cs",
            item("Cloud basics", topics=["aws-not-in-kafka"]),
            item("SQL joins", topics=["sql"], mode="lesson"),
            item("Storage", mode="mock", activities=["Watch a YouTube video"]),
        )])
        items = validate(data)["phases"][0]["items"]
        self.assertEqual([i["mode"] for i in items], ["lesson", "practice", "lesson"])
        self.assertTrue(all(i["activities"] == [] for i in items))

    def test_kafka_topics_named_by_the_item_are_linked_even_if_the_model_missed_them(self):
        names = {"oop": "Object-Oriented Programming", "dbms": "Database Management Systems", "sql": "SQL",
                 "arrays": "Arrays"}
        tracks = {"oop": "core-cs", "dbms": "core-cs", "sql": "core-cs", "arrays": "coding"}
        data = reply(sections=[section(
            "core_cs",
            item("OOP concepts in Java"),
            item("Normalisation", subtopics=["DBMS normal forms"]),
            item("Arrays in C"),  # a coding topic, not linkable from core CS
            item("Kubernetes basics"),
        )])
        items = validate_plan(data, jd_text=JD, topic_tracks=tracks, pattern_slugs=set(), topic_names=names,
                              sources=None)["phases"][0]["items"]
        self.assertEqual([(i["topics"], i["mode"]) for i in items], [
            (["oop"], "practice"), (["dbms"], "practice"), ([], "lesson"), ([], "lesson"),
        ])

    def test_interview_items_are_mocks_or_lessons_with_no_links(self):
        data = reply(sections=[section(
            "interview",
            item("HR round", mode="mock", topics=["arrays"]),
            item("Acme products", mode="lesson"),
            item("Technical round", mode="practice"),
        )])
        items = validate(data)["phases"][0]["items"]
        self.assertEqual([i["mode"] for i in items], ["mock", "lesson", "mock"])
        self.assertTrue(all(i["topics"] == [] and i["patterns"] == [] for i in items))
        self.assertEqual(items[0]["category"], "dsa")  # given category kept

    def test_values_are_normalised_or_defaulted(self):
        data = reply(sections=[section("coding",
                                       item(category="nonsense", importance="URGENT", hours=999, topics=["arrays"]),
                                       item(hours="abc", topics=["arrays"]))])
        first, second = validate(data)["phases"][0]["items"]
        self.assertEqual((first["category"], first["importance"], first["est_hours"]), ("dsa", "medium", Decimal("40")))
        self.assertEqual(second["est_hours"], Decimal("2"))

    def test_plan_without_usable_sections_is_rejected(self):
        with self.assertRaisesMessage(PlanRejected, "couldn't build a plan"):
            validate(reply(sections=[section("mock_interview", item())]))

    def test_sizes_are_capped(self):
        data = reply(sections=[section("coding", *[item(f"I{n}", topics=["arrays"]) for n in range(10)])])
        self.assertEqual(len(validate(data)["phases"][0]["items"]), services.MAX_ITEMS_PER_PHASE)

    def test_hours_are_scaled_to_the_students_budget(self):
        data = reply(sections=[section("coding", item(hours=10, topics=["arrays"]), item(hours=30, topics=["arrays"]))])
        items = validate(data, hours_budget=20)["phases"][0]["items"]
        self.assertEqual([i["est_hours"] for i in items], [Decimal("5"), Decimal("15")])

    def test_requirements_sorted_by_importance(self):
        data = reply(requirements=[
            requirement("SQL", "efficient SQL queries on PostgreSQL", importance="low"),
            requirement("REST APIs", "Design and implement RESTful APIs in Python and Django", importance="high"),
        ])
        self.assertEqual([r["skill"] for r in validate(data)["requirements"]], ["REST APIs", "SQL"])


class ResearchValidationTests(SimpleTestCase):
    def test_research_is_cleaned_and_carries_the_real_sources(self):
        clean = validate(reply(), company="Acme", sources=["GeeksforGeeks", "Glassdoor"])["research"]
        self.assertEqual(clean["basis"], "company")
        self.assertEqual(clean["rounds"][0]["name"], "Online assessment")
        self.assertEqual(clean["sources"], ["GeeksforGeeks", "Glassdoor"])

    def test_reports_about_a_differently_named_company_count_as_similar(self):
        clean = validate(reply(research=research(company_found="Wipfli")), company="Wifli")["research"]
        self.assertEqual(clean["basis"], "similar")
        same = validate(reply(research=research(company_found="Dell Technologies")), company="Dell")["research"]
        self.assertEqual(same["basis"], "company")

    def test_no_usable_research_is_stored_as_empty(self):
        empty = research(company_found="none", basis="none", summary="", rounds=[], frequently_asked=[])
        self.assertEqual(validate(reply(research=empty), company="Acme")["research"], {})

    def test_without_a_research_step_nothing_is_kept(self):
        self.assertEqual(validate(reply(), sources=None)["research"], {})


class ResearchStepTests(SimpleTestCase):
    def provider(self, *, supports=True, error=None, replies=None):
        replies = list(replies or ["Company found: Acme\nBasis: company\nRounds: OA, technical."])
        calls = []

        def research(**kwargs):
            calls.append(kwargs)
            if error:
                raise error
            text = replies.pop(0) if len(replies) > 1 else replies[0]
            return ResearchResult(text=text, sources=["Glassdoor"], result=LLMResult("end_turn", "m"))
        return SimpleNamespace(supports_research=supports, research=research, calls=calls)

    def test_research_result_is_returned(self):
        provider = self.provider()
        found = services.research_interviews(provider, role="SDE", company="Acme")
        self.assertEqual(found.sources, ["Glassdoor"])
        self.assertEqual(len(provider.calls), 1)

    def test_nothing_for_the_company_falls_back_to_similar_companies(self):
        provider = self.provider(replies=[
            "Company found: none\nBasis: none\nRounds: none",
            "Company found: Zebra, Cisco\nBasis: similar\nRounds: OA, technical, HR.",
        ])
        found = services.research_interviews(provider, role="SDE", company="Wifli", jd_text="Wifli builds WiFi analytics.")
        self.assertIn("Basis: similar", found.text)
        self.assertEqual(len(provider.calls), 2)
        self.assertIn("similar to it", provider.calls[1]["prompt"])
        self.assertIn("<job_excerpt>\nWifli builds WiFi analytics.\n</job_excerpt>", provider.calls[1]["prompt"])

    def test_no_usable_research_at_all_is_none(self):
        provider = self.provider(replies=["Company found: none\nBasis: none"])
        self.assertIsNone(services.research_interviews(provider, role="SDE", company="Wifli"))
        self.assertEqual(len(provider.calls), 2)

    def test_basis_is_read_from_the_report(self):
        self.assertEqual(services.research_basis("Company found: X\n**Basis:** Similar\n"), "similar")
        self.assertEqual(services.research_basis("no basis line"), "none")

    def test_providers_without_search_or_failures_plan_without_research(self):
        self.assertIsNone(services.research_interviews(self.provider(supports=False), role="SDE", company="Acme"))
        failing = self.provider(error=LLMError("busy", retryable=True))
        self.assertIsNone(services.research_interviews(failing, role="SDE", company="Acme"))

    @override_settings(PREP_RESEARCH=False)
    def test_research_can_be_switched_off(self):
        self.assertIsNone(services.research_interviews(self.provider(), role="SDE", company="Acme"))


class GroqResearchHelperTests(SimpleTestCase):
    def test_site_names_come_from_real_urls_and_skip_search_engines(self):
        self.assertEqual(site_name("https://www.geeksforgeeks.org/dell-interview"), "GeeksforGeeks")
        self.assertEqual(site_name("https://in.indeed.com/cmp/x"), "Indeed")
        self.assertEqual(site_name("https://dataford.io/guide"), "Dataford")
        self.assertEqual(site_name("https://www.ambitionbox.co.in/x"), "AmbitionBox")
        self.assertIsNone(site_name("https://exa.ai/search?q=x"))

    def test_sources_prefer_opened_pages_and_are_unique(self):
        tools = [
            {"type": "browser_search", "search_results": {"results": [
                {"url": "https://www.glassdoor.com/a"}, {"url": "https://www.glassdoor.com/b"}, {"url": "https://reddit.com/r"},
            ]}},
            {"type": "browser.open", "search_results": {"results": [{"url": "https://www.geeksforgeeks.org/x"}]}},
        ]
        self.assertEqual(sources_from(tools), ["GeeksforGeeks", "Glassdoor", "Reddit"])

    def test_citations_and_urls_are_stripped(self):
        self.assertEqual(clean_research_text("Rounds 【0†L13-L19】 see https://x.com/a now"), "Rounds see now")


class LessonValidationTests(SimpleTestCase):
    def lesson(self, **overrides):
        data = {
            "sections": [{"heading": "What", "body": "Storage basics."}, {"heading": "Why", "body": "RAID levels."}],
            "key_points": ["RAID 1 mirrors", "RAID 0 stripes"],
            "quiz": [{"question": f"Q{n}?", "options": ["A", "B", "C", "D"], "answer": 1, "explanation": "B."}
                     for n in range(5)],
        }
        data.update(overrides)
        return data

    def test_good_lesson_is_kept(self):
        clean = validate_lesson(self.lesson())
        self.assertEqual((len(clean["sections"]), len(clean["quiz"])), (2, 5))
        self.assertEqual(clean["quiz"][0]["answer"], 1)

    def test_broken_questions_are_dropped_and_too_few_fail(self):
        bad = [
            {"question": "Three options?", "options": ["A", "B", "C"], "answer": 0, "explanation": ""},
            {"question": "Answer out of range?", "options": ["A", "B", "C", "D"], "answer": 7, "explanation": ""},
            {"question": "Duplicate options?", "options": ["A", "A", "C", "D"], "answer": 0, "explanation": ""},
        ]
        with self.assertRaises(LLMError):
            validate_lesson(self.lesson(quiz=bad))
        with self.assertRaises(LLMError):
            validate_lesson(self.lesson(sections=[{"heading": "Only one", "body": "x"}]))
