# tests for models

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        # test creating a user with an email is successful
        email = "test@example.com"
        password = "testpassword"
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        # test email is normalized for a new user
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.com", "TEST3@example.com"],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "testpassword")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        # attemp to create a user without an email raises error
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "testpassword")

    def test_create_superuser(self):
        # test creating a superuser
        user = get_user_model().objects.create_superuser(
            "test@example.com", "testpassword"
        )

        self.assertTrue(user.is_superuser, True)
        self.assertTrue(user.is_staff, True)
