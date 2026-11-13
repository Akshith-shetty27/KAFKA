from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    def test_custom_user_model_is_active(self):
        self.assertEqual(User._meta.label, "accounts.User")
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_email_is_lowercased_and_password_hashed(self):
        user = User.objects.create_user("Asha@Example.COM", "s3cure-pass!")
        self.assertEqual(user.email, "asha@example.com")
        self.assertNotEqual(user.password, "s3cure-pass!")
        self.assertTrue(user.check_password("s3cure-pass!"))

    def test_email_must_be_unique_case_insensitively(self):
        User.objects.create_user("asha@example.com", "x")
        with self.assertRaises(IntegrityError):
            User.objects.create_user("ASHA@example.com", "y")

    def test_superuser_flags(self):
        admin = User.objects.create_superuser("admin@example.com", "x")
        self.assertTrue(admin.is_staff and admin.is_superuser)
