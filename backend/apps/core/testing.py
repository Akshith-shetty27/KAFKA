"""Shared test helpers: users, authenticated clients and a tiny catalog."""

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.catalog.models import Category, CodingDetail, Question, QuestionOption, Solution, Topic

User = get_user_model()

PASSWORD = "Str0ng-pass-phrase!"


def make_user(email="asha@example.com", password=PASSWORD, **extra):
    return User.objects.create_user(email=email, password=password, first_name=extra.pop("first_name", "Asha"), **extra)


def auth_client(user) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(user).access_token}")
    return client


def make_catalog():
    """Two categories, three topics, one question of each type (+ an unpublished one)."""
    coding = Category.objects.create(slug="coding", name="Coding", glyph="{ }", order=1)
    aptitude = Category.objects.create(slug="aptitude", name="Aptitude", glyph="Σ", order=2)

    arrays = Topic.objects.create(category=coding, slug="arrays", name="Arrays", order=1)
    strings = Topic.objects.create(category=coding, slug="strings", name="Strings", order=2)
    percentages = Topic.objects.create(category=aptitude, slug="percentages", name="Percentages", order=1)

    two_sum = Question.objects.create(
        topic=arrays, slug="two-sum", title="Two Sum", question_type="coding", difficulty="easy",
        statement="Find two numbers.", explanation="Use a hash map.", order=1,
    )
    CodingDetail.objects.create(question=two_sum, examples=[{"input": "x", "output": "y"}], approach="Hash it.")
    Solution.objects.create(question=two_sum, language="python", code="pass")
    Solution.objects.create(question=two_sum, language="java", code="class S {}")

    max_sub = Question.objects.create(
        topic=arrays, slug="max-subarray", title="Max Subarray", question_type="coding", difficulty="medium",
        statement="Kadane.", explanation="Extend or restart.", order=2,
    )
    CodingDetail.objects.create(question=max_sub, examples=[], approach="Kadane.")

    anagram = Question.objects.create(
        topic=strings, slug="anagram", title="Anagram", question_type="concept", difficulty="easy",
        statement="Explain anagram checking.", explanation="Count letters.", order=1,
    )

    pct = Question.objects.create(
        topic=percentages, slug="pct-q", title="Up and down", question_type="mcq", difficulty="easy",
        statement="+20% then -20%?", explanation="100 → 120 → 96.", order=1,
    )
    options = {
        label: QuestionOption.objects.create(question=pct, label=label, text=text, is_correct=(label == "B"))
        for label, text in [("A", "No change"), ("B", "4% decrease"), ("C", "4% increase")]
    }

    hidden = Question.objects.create(
        topic=percentages, slug="draft-q", title="Draft", question_type="concept", difficulty="hard",
        statement="Not ready.", explanation="", is_published=False,
    )
    return {
        "categories": {"coding": coding, "aptitude": aptitude},
        "questions": {"two_sum": two_sum, "max_sub": max_sub, "anagram": anagram, "pct": pct, "hidden": hidden},
        "options": options,
    }
