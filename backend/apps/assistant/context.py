"""
Question context for ASK KAFKA, built from the database — never from text the
browser sends, so a student can't smuggle a different "problem" in.

The anti-spoiler rule is enforced here, by what the model is *given*:

    mode / state                         model sees the solution?
    ------------------------------------ ------------------------
    chat or hint, question not completed  no  (statement, examples, constraints only)
    explain or review                     yes (a deliberate request)
    question already completed            yes

For MCQs, `explain` and `review` are only allowed after the student has
answered — otherwise ASK KAFKA would be a way around server-side grading.
"""

from dataclasses import dataclass

from rest_framework.exceptions import ValidationError

from apps.catalog.models import Question, QuestionType
from apps.progress.models import QuestionProgress

from .models import Mode


@dataclass(frozen=True)
class Capabilities:
    hint: bool
    explain: bool
    review: bool

    def as_dict(self):
        return {"hint": self.hint, "explain": self.explain, "review": self.review}


def _progress(user, question):
    return QuestionProgress.objects.filter(user=user, question=question).select_related("selected_option").first()


def capabilities(user, question: Question | None) -> Capabilities:
    if question is None:
        return Capabilities(hint=False, explain=False, review=False)
    progress = _progress(user, question)
    answered = bool(progress and progress.answer_count)
    if question.question_type == QuestionType.MCQ:
        return Capabilities(hint=not answered, explain=answered, review=answered)
    return Capabilities(hint=True, explain=True, review=False)


def check_mode_allowed(user, question: Question | None, mode: str) -> None:
    if mode == Mode.CHAT:
        return
    if question is None:
        raise ValidationError({"mode": ["Hints and explanations need a question. Open ASK KAFKA from a question page."]})
    caps = capabilities(user, question)
    if not getattr(caps, mode):
        messages = {
            Mode.HINT: "You've already answered this question — ask KAFKA to explain it instead.",
            Mode.EXPLAIN: "Answer the question first, then ask KAFKA to explain it.",
            Mode.REVIEW: "Reviewing an answer is available after you answer a multiple-choice question.",
        }
        raise ValidationError({"mode": [messages[mode]]})


def build_question_context(user, question: Question, mode: str) -> tuple[str, bool]:
    """Return (context text, whether the solution was included)."""
    question = (
        Question.objects.select_related("topic__category", "coding")
        .prefetch_related("patterns", "solutions", "options")
        .get(pk=question.pk)
    )
    progress = _progress(user, question)
    completed = bool(progress and progress.status == QuestionProgress.Status.COMPLETED)
    reveal = mode in (Mode.EXPLAIN, Mode.REVIEW) or completed

    lines = [
        "## Current question",
        f"Title: {question.title}",
        f"Track: {question.topic.category.name} / {question.topic.name}",
        f"Type: {question.get_question_type_display()} · Difficulty: {question.difficulty}",
    ]
    patterns = ", ".join(p.name for p in question.patterns.all())
    if patterns and reveal:
        lines.append(f"Patterns: {patterns}")
    lines += ["", "### Statement", question.statement]

    coding = getattr(question, "coding", None) if question.question_type == QuestionType.CODING else None
    if coding:
        if coding.examples:
            lines += ["", "### Examples"]
            for i, ex in enumerate(coding.examples, 1):
                lines.append(f"{i}. Input: {ex.get('input', '')} → Output: {ex.get('output', '')}")
                if ex.get("explanation"):
                    lines.append(f"   ({ex['explanation']})")
        if coding.constraints:
            lines += ["", "### Constraints", coding.constraints]

    options = list(question.options.all()) if question.question_type == QuestionType.MCQ else []
    if options:
        lines += ["", "### Options"]
        for o in options:
            mark = " (correct)" if reveal and o.is_correct else ""
            lines.append(f"{o.label}. {o.text}{mark}")

    if reveal:
        if coding and coding.approach:
            lines += ["", "### Reference approach", coding.approach]
        if question.explanation:
            lines += ["", "### Reference explanation", question.explanation]
        for s in question.solutions.all():
            lines += ["", f"### Reference solution ({s.get_language_display()})", f"```{s.language}", s.code, "```"]
    else:
        lines += ["", "(The reference solution is deliberately withheld. Do not invent or reveal a full solution.)"]

    lines += ["", "## Student's progress on this question"]
    if not progress:
        lines.append("Not started.")
    else:
        lines.append(f"Status: {progress.status}.")
        if progress.answer_count and progress.selected_option:
            verdict = "correct" if progress.is_correct else "incorrect"
            lines.append(
                f"Their latest answer: {progress.selected_option.label}. {progress.selected_option.text} ({verdict}); "
                f"{progress.answer_count} answer(s) so far."
            )
    return "\n".join(lines), reveal
