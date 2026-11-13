"""
Account business logic. Views call these functions; they never touch tokens
or models directly.
"""

from dataclasses import dataclass

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from django.db import transaction
from rest_framework import exceptions
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@dataclass(frozen=True)
class TokenPair:
    access: str
    refresh: str


class SessionExpired(exceptions.AuthenticationFailed):
    default_detail = "Your session has expired. Please sign in again."
    default_code = "session_expired"


def issue_tokens(user) -> TokenPair:
    refresh = RefreshToken.for_user(user)
    return TokenPair(access=str(refresh.access_token), refresh=str(refresh))


@transaction.atomic
def register_user(*, email, password, first_name="", last_name="", timezone=None) -> User:
    user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
    if timezone:
        user.profile.timezone = timezone
        user.profile.save(update_fields=["timezone", "updated_at"])
    return user


def login(*, request, email, password) -> User:
    user = authenticate(request, email=email.lower(), password=password)
    if user is None:
        # Same message whether the email exists or not, so the endpoint can't
        # be used to discover which emails are registered.
        raise exceptions.AuthenticationFailed("Incorrect email or password.", code="invalid_credentials")
    update_last_login(None, user)
    return user


def rotate_refresh_token(raw_refresh: str | None) -> TokenPair:
    """Exchange a refresh token for a new access token and a new refresh token.

    The old refresh token is blacklisted, so a stolen-and-replayed token stops
    working as soon as the real user refreshes.
    """
    if not raw_refresh:
        raise SessionExpired("You are not signed in.", code="not_signed_in")
    serializer = TokenRefreshSerializer(data={"refresh": raw_refresh})
    try:
        serializer.is_valid(raise_exception=True)
    except (TokenError, User.DoesNotExist):
        raise SessionExpired()
    except exceptions.AuthenticationFailed:
        raise SessionExpired("This account is disabled.", code="account_disabled")
    return TokenPair(access=serializer.validated_data["access"], refresh=serializer.validated_data["refresh"])


def logout(raw_refresh: str | None) -> None:
    """Blacklist the refresh token. Logging out twice is not an error."""
    if not raw_refresh:
        return
    try:
        RefreshToken(raw_refresh).blacklist()
    except TokenError:
        pass


@transaction.atomic
def change_password(*, user, new_password) -> TokenPair:
    """Set a new password, sign out every other session, return fresh tokens.

    All of the user's outstanding refresh tokens are blacklisted, so a device
    signed in with the old password loses access at its next refresh.
    """
    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

    user.set_password(new_password)
    user.save(update_fields=["password"])
    for token in OutstandingToken.objects.filter(user=user).exclude(blacklistedtoken__isnull=False):
        BlacklistedToken.objects.get_or_create(token=token)
    return issue_tokens(user)
