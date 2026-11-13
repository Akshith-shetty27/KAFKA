"""
Helpers for the refresh-token cookie.

The refresh token is long-lived, so it is kept where JavaScript can't read it:
an httpOnly cookie scoped to /api/v1/auth/ (it is never sent to other API
paths). SameSite=Lax stops other sites from triggering refresh/logout with it.
"""

from django.conf import settings
from rest_framework_simplejwt.settings import api_settings as jwt_settings


def set_refresh_cookie(response, refresh_token: str):
    response.set_cookie(
        settings.REFRESH_COOKIE_NAME,
        refresh_token,
        max_age=int(jwt_settings.REFRESH_TOKEN_LIFETIME.total_seconds()),
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        path=settings.REFRESH_COOKIE_PATH,
    )


def clear_refresh_cookie(response):
    response.delete_cookie(
        settings.REFRESH_COOKIE_NAME,
        path=settings.REFRESH_COOKIE_PATH,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
    )


def get_refresh_cookie(request) -> str | None:
    return request.COOKIES.get(settings.REFRESH_COOKIE_NAME) or None
