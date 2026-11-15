"""Settings for `python manage.py test --settings=config.settings.test`."""

from .base import *  # noqa: F401,F403

DEBUG = False
REFRESH_COOKIE_SECURE = False

# Hashing passwords with PBKDF2 is deliberately slow; tests don't need that.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Never call a real LLM from tests.
LLM_PROVIDER = "fake"
LLM_FAKE_DELAY = 0.0

# Tests deliberately trigger 4xx responses; don't print a warning for each.
LOGGING["loggers"] = {"django.request": {"level": "ERROR"}}  # noqa: F405

# Keep throttles out of the way of ordinary tests (throttling has its own test).
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_THROTTLE_RATES": {"auth": "1000/min", "auth_refresh": "1000/min", "assistant": "1000/min", "prep_plan": "1000/min"},
}
