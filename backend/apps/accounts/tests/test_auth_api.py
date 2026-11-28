from unittest import mock

from django.conf import settings
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.core.testing import PASSWORD, auth_client, make_user

COOKIE = settings.REFRESH_COOKIE_NAME


class RegisterTests(APITestCase):
    url = reverse("auth-register")

    def test_register_creates_user_profile_and_session(self):
        response = self.client.post(
            self.url,
            {"email": "New@Example.com", "password": PASSWORD, "first_name": "Ravi", "timezone": "Asia/Kolkata"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertIn("access", body)
        self.assertNotIn("refresh", body)  # refresh token never appears in JSON
        self.assertEqual(body["user"]["email"], "new@example.com")
        self.assertEqual(body["user"]["profile"]["timezone"], "Asia/Kolkata")

        cookie = response.cookies[COOKIE]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["path"], "/api/v1/auth/")
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertTrue(User.objects.get(email="new@example.com").check_password(PASSWORD))

    def test_duplicate_email_is_rejected_case_insensitively(self):
        make_user("ravi@example.com")
        response = self.client.post(
            self.url, {"email": "RAVI@example.com", "password": PASSWORD, "first_name": "R"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "validation_error")
        self.assertIn("email", response.json()["error"]["fields"])

    def test_weak_password_is_rejected(self):
        response = self.client.post(
            self.url, {"email": "a@example.com", "password": "12345678", "first_name": "A"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.json()["error"]["fields"])

    def test_invalid_timezone_is_rejected(self):
        response = self.client.post(
            self.url,
            {"email": "a@example.com", "password": PASSWORD, "first_name": "A", "timezone": "Mars/Base"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("timezone", response.json()["error"]["fields"])


class LoginTests(APITestCase):
    url = reverse("auth-login")

    def setUp(self):
        self.user = make_user()

    def test_login_success_returns_access_and_sets_cookie(self):
        response = self.client.post(self.url, {"email": "ASHA@example.com", "password": PASSWORD}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn(COOKIE, response.cookies)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)

    def test_wrong_password_is_401_with_generic_message(self):
        response = self.client.post(self.url, {"email": "asha@example.com", "password": "nope"}, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "invalid_credentials")

    def test_unknown_email_gets_the_same_response(self):
        response = self.client.post(self.url, {"email": "ghost@example.com", "password": "nope"}, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["message"], "Incorrect email or password.")

    def test_inactive_user_cannot_log_in(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.url, {"email": "asha@example.com", "password": PASSWORD}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_login_is_rate_limited(self):
        cache.clear()
        with mock.patch.object(ScopedRateThrottle, "THROTTLE_RATES", {"auth": "3/min"}):
            codes = [
                self.client.post(self.url, {"email": "asha@example.com", "password": "bad"}, format="json").status_code
                for _ in range(4)
            ]
        cache.clear()
        self.assertEqual(codes, [401, 401, 401, 429])


class RefreshAndLogoutTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        login = self.client.post(reverse("auth-login"), {"email": "asha@example.com", "password": PASSWORD}, format="json")
        self.original_refresh = login.cookies[COOKIE].value

    def test_refresh_rotates_token_and_blacklists_the_old_one(self):
        first = self.client.post(reverse("auth-refresh"))
        self.assertEqual(first.status_code, 200)
        self.assertIn("access", first.json())
        rotated = first.cookies[COOKIE].value
        self.assertNotEqual(rotated, self.original_refresh)

        # Replaying the old refresh token must fail.
        self.client.cookies[COOKIE] = self.original_refresh
        replay = self.client.post(reverse("auth-refresh"))
        self.assertEqual(replay.status_code, 401)
        self.assertEqual(replay.json()["error"]["code"], "session_expired")
        self.assertEqual(replay.cookies[COOKIE].value, "")  # cookie cleared

    def test_refresh_without_cookie_is_401(self):
        self.client.cookies.clear()
        response = self.client.post(reverse("auth-refresh"))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "not_signed_in")

    def test_refresh_ignores_an_expired_access_header(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
        self.assertEqual(self.client.post(reverse("auth-refresh")).status_code, 200)

    def test_logout_blacklists_refresh_and_clears_cookie(self):
        response = self.client.post(reverse("auth-logout"))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.cookies[COOKIE].value, "")
        self.client.cookies[COOKIE] = self.original_refresh
        self.assertEqual(self.client.post(reverse("auth-refresh")).status_code, 401)

    def test_logout_twice_is_harmless(self):
        self.client.post(reverse("auth-logout"))
        self.assertEqual(self.client.post(reverse("auth-logout")).status_code, 204)


class MeTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.client = auth_client(self.user)

    def test_me_requires_authentication(self):
        response = APIClient().get(reverse("auth-me"))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "not_authenticated")

    def test_get_me(self):
        body = self.client.get(reverse("auth-me")).json()
        self.assertEqual(body["email"], "asha@example.com")
        self.assertEqual(body["profile"]["daily_goal"], 5)
        self.assertEqual(body["profile"]["theme"], "ink")

    def test_patch_me_updates_user_and_profile(self):
        response = self.client.patch(
            reverse("auth-me"),
            {"last_name": "Rao", "profile": {"college": "NITK", "daily_goal": 8, "theme": "news"}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, "Rao")
        self.assertEqual(self.user.profile.college, "NITK")
        self.assertEqual(self.user.profile.daily_goal, 8)

    def test_email_cannot_be_changed_via_patch(self):
        self.client.patch(reverse("auth-me"), {"email": "evil@example.com"}, format="json")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "asha@example.com")

    def test_profile_validation(self):
        response = self.client.patch(reverse("auth-me"), {"profile": {"daily_goal": 0}}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_all_five_themes_can_be_chosen(self):
        for theme in ("ink", "news", "floral", "forest", "anime"):
            with self.subTest(theme=theme):
                response = self.client.patch(reverse("auth-me"), {"profile": {"theme": theme}}, format="json")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["profile"]["theme"], theme)

    def test_unknown_or_retired_theme_is_rejected(self):
        for theme in ("neon", "paper"):  # "paper" was the retired Cream theme
            with self.subTest(theme=theme):
                response = self.client.patch(reverse("auth-me"), {"profile": {"theme": theme}}, format="json")
                self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.theme, "ink")


class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.old_refresh = str(RefreshToken.for_user(self.user))  # another device's session
        self.client = auth_client(self.user)

    def test_change_password_signs_out_other_sessions(self):
        response = self.client.post(
            reverse("auth-change-password"),
            {"current_password": PASSWORD, "new_password": "An0ther-long-phrase"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(COOKIE, response.cookies)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("An0ther-long-phrase"))

        self.client.cookies[COOKIE] = self.old_refresh
        self.assertEqual(self.client.post(reverse("auth-refresh")).status_code, 401)

    def test_wrong_current_password(self):
        response = self.client.post(
            reverse("auth-change-password"),
            {"current_password": "wrong", "new_password": "An0ther-long-phrase"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("current_password", response.json()["error"]["fields"])


class ProfileSignalTests(APITestCase):
    def test_superuser_also_gets_a_profile(self):
        admin = User.objects.create_superuser("root@example.com", PASSWORD)
        self.assertEqual(admin.profile.timezone, "UTC")
