"""
Personalised study plans generated from a job description and web research
into the company's past interview experiences.

    PreparationPlan (one per generation; the pasted JD is kept as text)
      └─ PlanPhase — a section: Coding · Aptitude · Core CS · Interview prep
           └─ PlanItem — one thing to prepare, done entirely inside KAFKA:
                practice  linked KAFKA topics/patterns (the question bank)
                lesson    a topic KAFKA's bank doesn't cover: an AI-written note
                          and quiz, generated on demand and stored on the item
                mock      an Ask KAFKA mock interview for that round

Requirements extracted from the JD are stored on the plan as validated JSON
(each one carries an evidence quote from the JD), as is the interview research
(rounds, most-asked topics, source site names). Item links point at real
catalog rows, so a plan never sends a student to content that doesn't exist.
Progress on a plan is the items the student ticks off.

Plans made before sections existed keep their phases (fundamentals → … →
mock interviews) and free-text activities; they still display as they were.
"""

from django.conf import settings
from django.db import models

from apps.catalog.models import Pattern, Topic
from apps.core.models import TimeStampedModel


class Importance(models.TextChoices):
    HIGH = "high", "High"
    MEDIUM = "medium", "Medium"
    LOW = "low", "Low"


class SkillCategory(models.TextChoices):
    DSA = "dsa", "Data structures & algorithms"
    PROGRAMMING = "programming", "Programming languages"
    CS_FUNDAMENTALS = "cs_fundamentals", "CS fundamentals"
    DATABASES = "databases", "Databases & SQL"
    SYSTEM_DESIGN = "system_design", "System design"
    WEB = "web", "Web & APIs"
    CLOUD_DEVOPS = "cloud_devops", "Cloud & DevOps"
    DATA_ML = "data_ml", "Data, analytics & ML"
    TOOLS = "tools", "Tools & practices"
    APTITUDE = "aptitude", "Aptitude"
    COMMUNICATION = "communication", "Communication & behavioural"
    DOMAIN = "domain", "Domain & business knowledge"


class PreparationPlan(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="preparation_plans")
    role = models.CharField(max_length=120)
    company = models.CharField(max_length=120, blank=True)
    job_description = models.TextField(help_text="The description as pasted by the student.")
    jd_truncated = models.BooleanField(default=False, help_text="Only the first part was sent to the model.")
    candidate_info = models.TextField(blank=True, help_text="Optional background the student shared.")
    days_available = models.PositiveSmallIntegerField(null=True, blank=True)
    hours_per_day = models.PositiveSmallIntegerField(null=True, blank=True)

    summary = models.TextField()
    requirements = models.JSONField(default=list, help_text="[{skill, category, importance, evidence}] — validated.")
    research = models.JSONField(
        default=dict, blank=True,
        help_text="{company_found, basis, summary, rounds[{name, details}], frequently_asked[], sources[]} — "
        "past interview experiences found on the web; empty if research wasn't possible.",
    )

    provider = models.CharField(max_length=32)
    model = models.CharField(max_length=100)
    input_tokens = models.PositiveIntegerField(null=True, blank=True)
    output_tokens = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["user", "-created_at"], name="prep_plan_user_recent")]

    def __str__(self):
        return f"{self.role} @ {self.company}" if self.company else self.role


class PlanPhase(models.Model):
    class Kind(models.TextChoices):
        # Sections (current plans), in display order.
        CODING = "coding", "Coding"
        APTITUDE = "aptitude", "Aptitude"
        CORE_CS = "core_cs", "Core CS"
        INTERVIEW = "interview", "Interview prep"
        # Phases of plans made before sections existed.
        FUNDAMENTALS = "fundamentals", "Fundamentals"
        TECHNICAL = "technical", "Core technical skills"
        ADVANCED = "advanced", "Advanced topics"
        COMPANY = "company", "Company & role specific"
        MOCK_INTERVIEW = "mock_interview", "Mock interviews"

    plan = models.ForeignKey(PreparationPlan, on_delete=models.CASCADE, related_name="phases")
    order = models.PositiveSmallIntegerField()
    kind = models.CharField(max_length=20, choices=Kind.choices)
    title = models.CharField(max_length=160)
    goal = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]
        constraints = [models.UniqueConstraint(fields=["plan", "order"], name="unique_phase_order_per_plan")]

    def __str__(self):
        return self.title


class PlanItem(models.Model):
    class Mode(models.TextChoices):
        PRACTICE = "practice", "Practise in KAFKA"
        LESSON = "lesson", "Learn it in KAFKA"
        MOCK = "mock", "Mock interview"

    phase = models.ForeignKey(PlanPhase, on_delete=models.CASCADE, related_name="items")
    order = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=SkillCategory.choices)
    importance = models.CharField(max_length=10, choices=Importance.choices)
    reason = models.TextField(help_text="Why this matters for this job description.")
    subtopics = models.JSONField(default=list)
    activities = models.JSONField(default=list, help_text="Free-text activities (plans made before sections only).")
    mode = models.CharField(max_length=10, choices=Mode.choices, default=Mode.PRACTICE)
    lesson = models.JSONField(
        null=True, blank=True,
        help_text="For lesson items, once generated: {sections[{heading, body}], key_points[], quiz[{question, "
        "options[4], answer, explanation}], model}.",
    )
    est_hours = models.DecimalField(max_digits=4, decimal_places=1)
    topics = models.ManyToManyField(Topic, blank=True, related_name="plan_items")
    patterns = models.ManyToManyField(Pattern, blank=True, related_name="plan_items")
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["order"]
        constraints = [models.UniqueConstraint(fields=["phase", "order"], name="unique_item_order_per_phase")]

    @property
    def completed(self) -> bool:
        return self.completed_at is not None

    def __str__(self):
        return self.title
