"""
Preparation content: Category → Topic → Question.

A question's category is always reached through its topic; it is never
stored twice. Type-specific data lives in side tables so `Question` doesn't
carry columns that are empty for most rows:

    coding  → CodingDetail (1:1) + Solution (per language)
    mcq     → QuestionOption (2–6, exactly one correct)
    concept → explanation is the answer; SQL concepts may also have a Solution
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.core.models import TimeStampedModel


class Difficulty(models.TextChoices):
    EASY = "easy", "Easy"
    MEDIUM = "medium", "Medium"
    HARD = "hard", "Hard"


class QuestionType(models.TextChoices):
    CODING = "coding", "Coding problem"
    MCQ = "mcq", "Multiple choice"
    CONCEPT = "concept", "Concept question"


class Category(models.Model):
    slug = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    glyph = models.CharField(max_length=8, blank=True, help_text="Typographic glyph shown in the UI, e.g. { } or Σ.")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class TopicSection(models.Model):
    """Optional grouping of topics inside a category (e.g. Quantitative Aptitude)."""

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="sections")
    slug = models.SlugField(max_length=60)
    name = models.CharField(max_length=80)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["category__order", "order", "name"]
        constraints = [models.UniqueConstraint(fields=["category", "slug"], name="unique_section_slug_per_category")]

    def __str__(self):
        return f"{self.category.name} / {self.name}"


class Topic(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="topics")
    section = models.ForeignKey(
        TopicSection, on_delete=models.SET_NULL, null=True, blank=True, related_name="topics"
    )
    slug = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["category__order", "order", "name"]

    def clean(self):
        if self.section_id and self.section.category_id != self.category_id:
            raise ValidationError({"section": "Section must belong to the same category as the topic."})

    def __str__(self):
        return self.name


class Pattern(models.Model):
    """Cross-cutting problem-solving pattern (Two Pointers, Sliding Window, …)."""

    slug = models.SlugField(max_length=60, unique=True)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Question(TimeStampedModel):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="questions")
    slug = models.SlugField(max_length=120, unique=True)
    title = models.CharField(max_length=200)
    question_type = models.CharField(max_length=10, choices=QuestionType.choices)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices)
    statement = models.TextField(help_text="Markdown.")
    explanation = models.TextField(blank=True, help_text="Markdown. For MCQs it is revealed only after answering.")
    patterns = models.ManyToManyField(Pattern, blank=True, related_name="questions")
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["topic__category__order", "topic__order", "order", "id"]
        indexes = [
            models.Index(fields=["topic", "order"]),
            models.Index(fields=["difficulty"]),
            models.Index(fields=["question_type"]),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(difficulty__in=Difficulty.values), name="question_valid_difficulty"),
            models.CheckConstraint(condition=Q(question_type__in=QuestionType.values), name="question_valid_type"),
        ]

    def __str__(self):
        return self.title

    @property
    def category(self):
        return self.topic.category


class CodingDetail(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, primary_key=True, related_name="coding")
    constraints = models.TextField(blank=True, help_text="Markdown list of input constraints.")
    # Ordered list of {"input": str, "output": str, "explanation": str}. Stored
    # as JSON because examples are only ever read together with their question.
    examples = models.JSONField(default=list, blank=True)
    approach = models.TextField(help_text="Markdown. How to think about the problem.")
    time_complexity = models.CharField(max_length=64, blank=True)
    space_complexity = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f"Coding detail: {self.question}"


class Solution(models.Model):
    class Language(models.TextChoices):
        PYTHON = "python", "Python"
        JAVA = "java", "Java"
        CPP = "cpp", "C++"
        JAVASCRIPT = "javascript", "JavaScript"
        SQL = "sql", "SQL"

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="solutions")
    language = models.CharField(max_length=16, choices=Language.choices)
    code = models.TextField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["question", "language"]
        constraints = [
            models.UniqueConstraint(fields=["question", "language"], name="unique_solution_language_per_question")
        ]

    def __str__(self):
        return f"{self.question} ({self.get_language_display()})"


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    label = models.CharField(max_length=1)  # A, B, C, ...
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["question", "label"]
        constraints = [
            models.UniqueConstraint(fields=["question", "label"], name="unique_option_label_per_question"),
            # Partial unique index: at most one correct option per question.
            models.UniqueConstraint(
                fields=["question"], condition=Q(is_correct=True), name="one_correct_option_per_question"
            ),
        ]

    def __str__(self):
        return f"{self.label}. {self.text[:40]}"
