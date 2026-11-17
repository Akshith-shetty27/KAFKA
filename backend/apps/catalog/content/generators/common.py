"""
Shared helpers for aptitude generators.

A generator is a function `(rng) -> Item | None` for one question *shape*.
It picks numbers, computes the answer with exact arithmetic (`Fraction`),
checks it a second way where possible, and builds plausible wrong options
from typical mistakes. Returning None means "these numbers don't give a
clean question — try again".
"""

import random
import textwrap
from dataclasses import dataclass, field
from fractions import Fraction
from string import ascii_uppercase


@dataclass
class Item:
    title: str
    statement: str
    answer: str  # display text of the correct option
    distractors: list[str]  # candidate wrong options (deduplicated later)
    explanation: str
    key: tuple = field(default=())  # identifies the underlying question, for duplicate detection


@dataclass(frozen=True)
class Template:
    name: str  # short slug fragment, e.g. "successive"
    difficulty: str  # easy | medium | hard
    make: object  # (rng) -> Item | None


class Retry(Exception):
    """Raised inside a generator when the sampled numbers don't work."""


def need(condition: bool) -> None:
    if not condition:
        raise Retry


# --- numbers -------------------------------------------------------------------

def is_nice(x, places: int = 2) -> bool:
    """True if x has at most `places` decimal places (exactly)."""
    x = Fraction(x)
    return (x * 10**places).denominator == 1


def num(x, places: int = 2) -> str:
    """Exact value → display: 16000 → '16,000', 12.5 → '12.5', 2/3 → '0.67' (only if forced)."""
    x = Fraction(x)
    if x.denominator == 1:
        return f"{int(x):,}"
    value = round(float(x), places)
    text = f"{value:,.{places}f}".rstrip("0").rstrip(".")
    return text


def rupees(x) -> str:
    return f"₹{num(x)}"


def pct(x) -> str:
    return f"{num(x)}%"


def ratio(*parts) -> str:
    return " : ".join(num(p) for p in parts)


def nice_neighbours(value, rng: random.Random, fmt=num, steps=(1, 2, 5, 10)) -> list[str]:
    """Wrong options close to the right answer (used to top up mistake-based distractors)."""
    value = Fraction(value)
    out = []
    base = max(abs(value) / 10, 1)
    for step in steps:
        delta = Fraction(round(base * step / 5)) or Fraction(step)
        for candidate in (value + delta, value - delta):
            if candidate > 0:
                out.append(fmt(candidate))
    rng.shuffle(out)
    return out


# --- assembling a question -------------------------------------------------------

def build_options(item: Item, rng: random.Random, count: int = 4) -> tuple[list[str], str]:
    """Correct answer + `count - 1` distinct wrong options, shuffled. Returns (options, answer label)."""
    wrong = []
    for d in item.distractors:
        if d != item.answer and d not in wrong and d.strip():
            wrong.append(d)
    need(len(wrong) >= count - 1)
    options = wrong[: count - 1] + [item.answer]
    rng.shuffle(options)
    return options, ascii_uppercase[options.index(item.answer)]


def _signature(statement: str) -> str:
    """What makes two questions 'the same': the bold part (e.g. a series) if any, else the whole text."""
    import re

    bold = re.findall(r"\*\*(.+?)\*\*", statement)
    return "|".join(bold) if bold and len(" ".join(bold)) > 12 else " ".join(statement.split())


def generate_topic(*, topic: str, prefix: str, templates: list[Template], targets: dict[str, int],
                   seed: int, existing_statements: set[str] = frozenset()) -> list[dict]:
    """Produce `targets[difficulty]` questions per difficulty, cycling through that difficulty's templates."""
    rng = random.Random(f"{topic}:{seed}")
    out, seen_keys, seen_titles = [], set(), set()
    seen_statements = {_signature(s) for s in existing_statements}
    counters: dict[str, int] = {}
    for difficulty in ("easy", "medium", "hard"):
        pool = [t for t in templates if t.difficulty == difficulty]
        wanted = targets.get(difficulty, 0)
        if wanted and not pool:
            raise ValueError(f"{topic}: no {difficulty} templates")
        made, attempts, i = 0, 0, 0
        while made < wanted:
            attempts += 1
            if attempts > 20000:
                raise ValueError(f"{topic}: couldn't generate enough {difficulty} questions")
            template = pool[i % len(pool)]
            try:
                item = template.make(rng)
                if item is None:
                    raise Retry
                key = (template.name, *item.key) if item.key else (template.name, item.statement)
                need(key not in seen_keys and _signature(item.statement) not in seen_statements and item.title not in seen_titles)
                options, label = build_options(item, rng)
            except Retry:
                if attempts % 50 == 0:
                    i += 1  # this template may be exhausted; move on
                continue
            seen_keys.add(key)
            seen_statements.add(_signature(item.statement))
            seen_titles.add(item.title)
            counters[template.name] = counters.get(template.name, 0) + 1
            out.append(
                {
                    "slug": f"{prefix}-{template.name}-{counters[template.name]}",
                    "title": item.title,
                    "type": "mcq",
                    "difficulty": difficulty,
                    "statement": " ".join(item.statement.split()),
                    "options": options,
                    "answer": label,
                    "explanation": textwrap.dedent(item.explanation).strip(),
                }
            )
            made += 1
            i += 1
    return out
