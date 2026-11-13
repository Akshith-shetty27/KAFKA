"""Settings for `python manage.py test --settings=config.settings.test`."""

from .base import *  # noqa: F401,F403

DEBUG = False
REFRESH_COOKIE_SECURE = False

# Hashing passwords with PBKDF2 is deliberately slow; tests don't need that.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Never call a real LLM from tests.
LLM_PROVIDER = "fake"
