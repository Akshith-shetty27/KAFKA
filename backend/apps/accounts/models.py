import zoneinfo

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """Manager for a user model that logs in with email instead of username."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # stores a salted hash, never the raw password
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not extra_fields["is_staff"] or not extra_fields["is_superuser"]:
            raise ValueError("Superuser must have is_staff=True and is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    KAFKA user. Email is the login identifier and is stored lower-cased so
    `Asha@x.com` and `asha@x.com` can't become two accounts.

    Everything that isn't about authentication lives on `UserProfile`.
    """

    username = None
    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email).lower()

    def __str__(self):
        return self.email


def validate_timezone(value):
    if value not in zoneinfo.available_timezones():
        raise ValidationError(f"'{value}' is not a valid IANA timezone (e.g. 'Asia/Kolkata').")


class UserProfile(TimeStampedModel):
    """Preparation preferences. Exactly one per user (created by a signal)."""

    class Language(models.TextChoices):
        PYTHON = "python", "Python"
        JAVA = "java", "Java"
        CPP = "cpp", "C++"
        JAVASCRIPT = "javascript", "JavaScript"

    class Theme(models.TextChoices):
        # "ink" is kept as the stored value for Space so existing profiles don't change.
        # Cream ("paper") was retired; migration 0003 moved its users to Space.
        INK = "ink", "Space (dark, starfield)"
        NEWS = "news", "Newspaper (light, editorial)"
        FLORAL = "floral", "Floral (dark, pink)"
        FOREST = "forest", "Forest (dark, mountain meadow)"
        ANIME = "anime", "Anime (twilight, sakura)"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    college = models.CharField(max_length=160, blank=True)
    graduation_year = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1990), MaxValueValidator(2100)]
    )
    target_role = models.CharField(max_length=120, blank=True)
    preferred_language = models.CharField(max_length=16, choices=Language.choices, default=Language.PYTHON)
    daily_goal = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text="Questions per day the student aims for; drives today's plan.",
    )
    timezone = models.CharField(
        max_length=64,
        default="UTC",
        validators=[validate_timezone],
        help_text="Used to decide what 'today' means for streaks and daily activity.",
    )
    theme = models.CharField(max_length=8, choices=Theme.choices, default=Theme.INK)

    def __str__(self):
        return f"Profile of {self.user}"

    @property
    def tzinfo(self):
        return zoneinfo.ZoneInfo(self.timezone)
