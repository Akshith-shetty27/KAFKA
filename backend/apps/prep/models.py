"""
Personalised study plans generated from a job description.

    PreparationPlan (one per generation; the pasted JD is kept as text)
      └─ PlanPhase (fundamentals → technical → advanced → company → mock interviews)
           └─ PlanItem (what to study, why, how, how long; links to catalog topics/patterns)

Requirements extracted from the JD are stored on the plan as validated JSON
(each one carries an evidence quote from the JD). Item links point at real
catalog rows, so a plan never sends a student to content that doesn't exist.
Progress on a plan is the items the student ticks off.
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
    phase = models.ForeignKey(PlanPhase, on_delete=models.CASCADE, related_name="items")
    order = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=SkillCategory.choices)
    importance = models.CharField(max_length=10, choices=Importance.choices)
    reason = models.TextField(help_text="Why this matters for this job description.")
    subtopics = models.JSONField(default=list)
    activities = models.JSONField(default=list)
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
