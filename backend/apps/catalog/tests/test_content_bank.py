"""
The expanded question bank: counts, format, and correctness.

Aptitude answers are generated with exact arithmetic; here a sample of
templates is re-solved *independently* — by parsing the question text, not by
calling the generator — and compared with the marked answer. Every coding
problem's reference solution is executed against its examples and hidden
cases.
"""

import math
import re
from collections import Counter
from fractions import Fraction
from io import StringIO
from string import ascii_uppercase

from django.core.management import call_command
from django.test import SimpleTestCase

from apps.catalog.content import aptitude, coding
from apps.catalog.content.bank.coding import all_problems, run_problem


def answer_text(q):
    return q["options"][ascii_uppercase.index(q["answer"])]


def number(text):
    """'₹16,000' / '12.5%' / '13 km' → Fraction."""
    match = re.search(r"-?[\d,]+(?:\.\d+)?", text)
    return Fraction(match.group().replace(",", ""))


def aptitude_questions():
    return [(t["slug"], q) for t in aptitude.CATEGORY["topics"] for q in t["questions"]]


class AptitudeBankTests(SimpleTestCase):
    def test_every_topic_has_20_easy_20_medium_10_hard(self):
        for topic in aptitude.CATEGORY["topics"]:
            counts = Counter(q["difficulty"] for q in topic["questions"])
            with self.subTest(topic=topic["slug"]):
                self.assertGreaterEqual(counts["easy"], 20)
                self.assertGreaterEqual(counts["medium"], 20)
                self.assertGreaterEqual(counts["hard"], 10)
                self.assertGreaterEqual(len(topic["questions"]), 50)

    def test_options_are_four_distinct_and_the_answer_is_one_of_them(self):
        for slug, q in aptitude_questions():
            with self.subTest(question=q["slug"]):
                self.assertEqual(len(q["options"]), 4)
                self.assertEqual(len(set(q["options"])), 4)
                self.assertIn(q["answer"], "ABCD")
                self.assertTrue(q["explanation"].strip())

    def test_no_duplicate_questions_within_a_topic(self):
        for topic in aptitude.CATEGORY["topics"]:
            # Same prompt with different options is a different question ("Choose the correct sentence.").
            statements = [(" ".join(q["statement"].split()), tuple(sorted(q["options"]))) for q in topic["questions"]]
            titles = [q["title"] for q in topic["questions"]]
            with self.subTest(topic=topic["slug"]):
                self.assertEqual(len(statements), len(set(statements)))
                self.assertEqual(len(titles), len(set(titles)))

    def test_generated_bank_matches_the_generators(self):
        out = StringIO()
        call_command("generate_aptitude", "--check", stdout=out)
        self.assertIn("up to date", out.getvalue())

    def test_answers_independently_recomputed(self):
        """Re-solve several templates from the question text alone."""
        checks = 0
        for _, q in aptitude_questions():
            s, slug, ans = q["statement"], q["slug"], answer_text(q)
            expected = None
            if re.fullmatch(r"cd-value-\d+", slug):
                word = re.search(r"\*\*(\w+)\*\*", s).group(1)
                expected = sum(ord(c) - 64 for c in word)
            elif re.fullmatch(r"cd-reverse-\d+", slug):
                expected = re.findall(r"\*\*(\w+)\*\*", s)[-1][::-1]
            elif re.fullmatch(r"cd-shift-\d+", slug):
                given, code, word = re.findall(r"\*\*(\w+)\*\*", s)
                k = (ord(code[0]) - ord(given[0])) % 26
                expected = "".join(chr((ord(c) - 65 + k) % 26 + 65) for c in word)
            elif re.fullmatch(r"int-si-\d+", slug):
                p, r, t = re.search(r"₹([\d,]+) at (\d+)% per annum for (\d+) years", s).groups()
                expected = Fraction(int(p.replace(",", "")) * int(r) * int(t), 100)
            elif re.fullmatch(r"int-ci-si-2y-\d+", slug):
                p, r = re.search(r"₹([\d,]+) at (\d+)%", s).groups()
                expected = int(p.replace(",", "")) * Fraction(int(r), 100) ** 2
            elif re.fullmatch(r"pct-of-number-\d+", slug):
                p, part = re.search(r"If (\d+)% of a number is ([\d,]+)", s).groups()
                expected = Fraction(int(part.replace(",", "")) * 100, int(p))
            elif re.fullmatch(r"ds-two-legs-\d+", slug):
                a, b = map(int, re.findall(r"(\d+) km", s))
                expected = math.isqrt(a * a + b * b)
            elif re.fullmatch(r"std-pole-\d+", slug):
                v, t = map(int, re.search(r"at (\d+) km/h passes a signal pole in (\d+) seconds", s).groups())
                expected = Fraction(v * 5, 18) * t
            elif re.fullmatch(r"avg-list-\d+", slug):
                values = list(map(int, re.search(r"average of ([\d, ]+)\.", s).group(1).split(", ")))
                expected = Fraction(sum(values), len(values))
            elif re.fullmatch(r"tw-together-\d+", slug):
                a, b = map(int, re.findall(r"in (\d+) days", s))
                expected = Fraction(a * b, a + b)
            elif re.fullmatch(r"ns-(arithmetic|geometric)-\d+", slug):
                terms = list(map(int, re.search(r"\*\*([\d, ]+), \?\*\*", s).group(1).split(", ")))
                diffs = {b - a for a, b in zip(terms, terms[1:])}
                expected = terms[-1] + diffs.pop() if len(diffs) == 1 else terms[-1] * (terms[1] // terms[0])
            if expected is None:
                continue
            checks += 1
            with self.subTest(question=slug):
                if isinstance(expected, str):
                    self.assertEqual(ans, expected)
                else:
                    self.assertEqual(number(ans), Fraction(expected))
        self.assertGreater(checks, 40)  # make sure the sample really ran


class CodingBankTests(SimpleTestCase):
    def test_every_topic_has_at_least_15_problems(self):
        topics = {t["slug"]: t["questions"] for t in coding.CATEGORY["topics"]}
        self.assertEqual(len(topics), 14)
        for slug, questions in topics.items():
            with self.subTest(topic=slug):
                self.assertGreaterEqual(len(questions), 15)

    def test_new_problems_are_complete(self):
        for topic, problems in all_problems().items():
            for p in problems:
                with self.subTest(problem=p["slug"]):
                    self.assertGreaterEqual(len(p["examples"]), 2)
                    self.assertIn("### Input", p["statement"])
                    self.assertIn("### Output", p["statement"])
                    self.assertTrue(p["constraints"] and p["approach"] and p["explanation"])
                    self.assertTrue(p["time"] and p["space"])
                    self.assertTrue(all(ex["input"] and ex["output"] for ex in p["examples"]))

    def test_reference_solutions_produce_the_expected_outputs(self):
        failures = []
        for problems in all_problems().values():
            for p in problems:
                failures += run_problem(p)
        self.assertEqual(failures, [])

    def test_slugs_are_unique_across_the_whole_catalog(self):
        from apps.catalog.content import core_cs

        slugs = [q["slug"] for m in (coding, aptitude, core_cs) for t in m.CATEGORY["topics"] for q in t["questions"]]
        self.assertEqual([s for s, n in Counter(slugs).items() if n > 1], [])
