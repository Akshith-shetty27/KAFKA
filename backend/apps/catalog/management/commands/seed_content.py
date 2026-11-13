"""
python manage.py seed_content

Loads the preparation content in `apps/catalog/content/` into the database.
Safe to run any number of times: rows are matched by slug and updated in
place, so existing user progress (which points at question/option ids) keeps
working after content edits. Nothing is deleted except solutions/options that
were removed from a question's content.

All content is validated before anything is written; one invalid question
aborts the whole run.
"""

import textwrap
from string import ascii_uppercase

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.catalog.content import aptitude, coding, core_cs
from apps.catalog.models import (
    Category,
    CodingDetail,
    Difficulty,
    Pattern,
    Question,
    QuestionOption,
    QuestionType,
    Solution,
    Topic,
    TopicSection,
)

CONTENT_MODULES = [coding, aptitude, core_cs]


def clean(text: str | None) -> str:
    """Content is written as indented triple-quoted strings; normalise it."""
    return textwrap.dedent(text or "").strip()


class ContentError(Exception):
    pass


def validate(categories: list[dict], patterns: list[dict]) -> None:
    errors = []
    pattern_slugs = {p["slug"] for p in patterns}
    topic_slugs, question_slugs = set(), set()

    for cat in categories:
        section_slugs = {s["slug"] for s in cat.get("sections", [])}
        for topic in cat["topics"]:
            where = f"{cat['slug']}/{topic['slug']}"
            if topic["slug"] in topic_slugs:
                errors.append(f"{where}: duplicate topic slug")
            topic_slugs.add(topic["slug"])
            if topic.get("section") and topic["section"] not in section_slugs:
                errors.append(f"{where}: unknown section '{topic['section']}'")

            for q in topic["questions"]:
                qwhere = f"{where}/{q.get('slug')}"
                if q["slug"] in question_slugs:
                    errors.append(f"{qwhere}: duplicate question slug")
                question_slugs.add(q["slug"])
                if q["type"] not in QuestionType.values:
                    errors.append(f"{qwhere}: bad type '{q['type']}'")
                if q["difficulty"] not in Difficulty.values:
                    errors.append(f"{qwhere}: bad difficulty '{q['difficulty']}'")
                for slug in q.get("patterns", []):
                    if slug not in pattern_slugs:
                        errors.append(f"{qwhere}: unknown pattern '{slug}'")
                if not clean(q.get("statement")):
                    errors.append(f"{qwhere}: missing statement")
                if not clean(q.get("explanation")):
                    errors.append(f"{qwhere}: missing explanation")
                for lang in q.get("solutions", {}):
                    if lang not in Solution.Language.values:
                        errors.append(f"{qwhere}: unknown solution language '{lang}'")

                if q["type"] == QuestionType.CODING:
                    if not clean(q.get("approach")):
                        errors.append(f"{qwhere}: coding question needs an approach")
                    if not q.get("examples"):
                        errors.append(f"{qwhere}: coding question needs examples")
                    if not q.get("solutions"):
                        errors.append(f"{qwhere}: coding question needs at least one solution")
                elif q["type"] == QuestionType.MCQ:
                    options = q.get("options", [])
                    if not 2 <= len(options) <= 6:
                        errors.append(f"{qwhere}: MCQ needs 2–6 options")
                    labels = ascii_uppercase[: len(options)]
                    if q.get("answer") not in labels:
                        errors.append(f"{qwhere}: answer '{q.get('answer')}' is not one of {list(labels)}")

    if errors:
        raise ContentError("\n".join(errors))


class Command(BaseCommand):
    help = "Load or update preparation content (categories, topics, questions). Idempotent."

    def handle(self, *args, **options):
        categories = [m.CATEGORY for m in CONTENT_MODULES]
        patterns = coding.PATTERNS
        try:
            validate(categories, patterns)
        except ContentError as exc:
            raise CommandError(f"Content is invalid; nothing was written.\n{exc}")

        self.stats = {"created": 0, "updated": 0}
        with transaction.atomic():
            pattern_map = self._load_patterns(patterns)
            for order, cat in enumerate(categories, start=1):
                self._load_category(cat, order, pattern_map)

        total = Question.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Content loaded: {self.stats['created']} questions created, "
                f"{self.stats['updated']} updated ({total} in database)."
            )
        )

    # --- loaders --------------------------------------------------------------

    def _load_patterns(self, patterns):
        result = {}
        for order, p in enumerate(patterns, start=1):
            obj, _ = Pattern.objects.update_or_create(
                slug=p["slug"],
                defaults={"name": p["name"], "description": clean(p.get("description")), "order": order},
            )
            result[p["slug"]] = obj
        return result

    def _load_category(self, cat, order, pattern_map):
        category, _ = Category.objects.update_or_create(
            slug=cat["slug"],
            defaults={
                "name": cat["name"],
                "description": clean(cat.get("description")),
                "glyph": cat.get("glyph", ""),
                "order": order,
            },
        )
        sections = {}
        for s_order, s in enumerate(cat.get("sections", []), start=1):
            sections[s["slug"]], _ = TopicSection.objects.update_or_create(
                category=category, slug=s["slug"], defaults={"name": s["name"], "order": s_order}
            )

        for t_order, t in enumerate(cat["topics"], start=1):
            topic, _ = Topic.objects.update_or_create(
                slug=t["slug"],
                defaults={
                    "category": category,
                    "section": sections.get(t.get("section")),
                    "name": t["name"],
                    "description": clean(t.get("description")),
                    "order": t_order,
                },
            )
            for q_order, q in enumerate(t["questions"], start=1):
                self._load_question(topic, q, q_order, pattern_map)

    def _load_question(self, topic, q, order, pattern_map):
        question, created = Question.objects.update_or_create(
            slug=q["slug"],
            defaults={
                "topic": topic,
                "title": q["title"],
                "question_type": q["type"],
                "difficulty": q["difficulty"],
                "statement": clean(q["statement"]),
                "explanation": clean(q.get("explanation")),
                "order": order,
                "is_published": q.get("published", True),
            },
        )
        self.stats["created" if created else "updated"] += 1
        question.patterns.set([pattern_map[s] for s in q.get("patterns", [])])

        # Coding detail
        if q["type"] == QuestionType.CODING:
            CodingDetail.objects.update_or_create(
                question=question,
                defaults={
                    "constraints": clean(q.get("constraints")),
                    "examples": [
                        {k: clean(v) for k, v in example.items()} for example in q.get("examples", [])
                    ],
                    "approach": clean(q["approach"]),
                    "time_complexity": q.get("time", ""),
                    "space_complexity": q.get("space", ""),
                },
            )
        else:
            CodingDetail.objects.filter(question=question).delete()

        # Solutions (matched by language)
        solutions = q.get("solutions", {})
        for language, code in solutions.items():
            Solution.objects.update_or_create(
                question=question, language=language, defaults={"code": clean(code)}
            )
        question.solutions.exclude(language__in=list(solutions)).delete()

        # Options (matched by label so progress.selected_option stays valid).
        # Clear is_correct first: the partial unique index allows only one
        # correct option at any moment, even mid-update.
        options = q.get("options", []) if q["type"] == QuestionType.MCQ else []
        question.options.update(is_correct=False)
        labels = []
        for label, text in zip(ascii_uppercase, options):
            labels.append(label)
            QuestionOption.objects.update_or_create(
                question=question,
                label=label,
                defaults={"text": clean(text), "is_correct": label == q.get("answer")},
            )
        question.options.exclude(label__in=labels).delete()
