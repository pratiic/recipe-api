# tests for user api
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    # create and return a new user
    user = get_user_model().objects.create_user(**params)
    return user


def get_payload(name="test user", email="test@example.com", password="testpassword"):
    return {"name": name, "email": email, "password": password}


class PublicUserApiTests(TestCase):
    # test public features of user api
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        # test creating a user is successful
        payload = get_payload()

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

        self.assertNotIn("password", res)

    def test_user_with_email_exists_error(self):
        # error if user with provided email already exists
        payload = get_payload()
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        # error if provided password less than 5 characters
        payload = get_payload(password="pass")

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        # test generates token for valid credentials
        pl = get_payload()
        create_user(**pl)

        res = self.client.post(
            TOKEN_URL,
            {
                "email": pl["email"],
                "password": pl["password"],
            },
        )

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        # test returns error if credentials are not valid
        payload = get_payload()
        create_user(**payload)

        res = self.client.post(
            TOKEN_URL,
            {
                "email": payload["email"],
                "password": "badpass",
            },
        )

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        # test authentication is required for users
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    # test API endpoints that require user authentication
    def setUp(self):
        self.user = create_user(**get_payload())
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        # test retrieving profile for authenticated users
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {"name": self.user.name, "email": self.user.email})

    def test_post_me_not_allowed(self):
        # test post is not allowed for me endpoint
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        # test user profile update for authenticated user
        payload = {"name": "updated name", "password": "new password"}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
