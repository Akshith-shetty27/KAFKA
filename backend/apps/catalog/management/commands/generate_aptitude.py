"""
python manage.py generate_aptitude [--check]

Regenerates the aptitude bank (`content/bank/aptitude/<topic>.json`) from the
templates in `content/generators/`, topping every topic up to
20 easy / 20 medium / 10 hard questions (hand-written ones count).

Generation is deterministic (seeded), so re-running produces identical files.
`--check` writes nothing and fails if the files are out of date — the test
suite runs it, so generator changes can't silently drift from the bank.
Then run `seed_content` to load the questions.
"""

import json
from collections import Counter

from django.core.management.base import BaseCommand, CommandError

from apps.catalog.content import aptitude
from apps.catalog.content.bank import APTITUDE_DIR
from apps.catalog.content.generators import logical, quant, verbal
from apps.catalog.content.generators.common import generate_topic

TARGETS = {"easy": 20, "medium": 20, "hard": 10}
SEED = 2026


def hand_written(topic_slug: str) -> list[dict]:
    topic = next(t for t in aptitude.HAND_WRITTEN_TOPICS if t["slug"] == topic_slug)
    return topic["questions"]


def build_all() -> dict[str, list[dict]]:
    out = {}
    generators = {**quant.TOPICS, **logical.TOPICS}
    for slug, (prefix, templates) in generators.items():
        existing = hand_written(slug)
        have = Counter(q["difficulty"] for q in existing)
        targets = {d: max(0, n - have[d]) for d, n in TARGETS.items()}
        statements = {" ".join(q["statement"].split()) for q in existing}
        out[slug] = generate_topic(topic=slug, prefix=prefix, templates=templates, targets=targets, seed=SEED,
                                   existing_statements=statements)
    for slug, questions in verbal.TOPICS.items():
        out[slug] = questions
    return out


def render(questions: list[dict]) -> str:
    return json.dumps(questions, ensure_ascii=False, indent=1) + "\n"


class Command(BaseCommand):
    help = "Generate the aptitude question bank (20 easy / 20 medium / 10 hard per topic)."

    def add_arguments(self, parser):
        parser.add_argument("--check", action="store_true", help="Fail if the bank files are out of date.")

    def handle(self, *args, check=False, **options):
        bank = build_all()
        stale = []
        for slug, questions in bank.items():
            path = APTITUDE_DIR / f"{slug}.json"
            text = render(questions)
            if check:
                if not path.exists() or path.read_text(encoding="utf-8") != text:
                    stale.append(slug)
            else:
                path.write_text(text, encoding="utf-8")
                total = Counter(q["difficulty"] for q in hand_written(slug) + questions)
                self.stdout.write(f"{slug}: +{len(questions)} → {dict(total)}")
        if stale:
            raise CommandError(f"Aptitude bank is out of date for: {', '.join(stale)}. Run generate_aptitude.")
        if check:
            self.stdout.write(self.style.SUCCESS("Aptitude bank is up to date."))
