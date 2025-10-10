"""
Tests Account Module APIs
"""
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

AUTH_URL = reverse("account:otp")
# LOGOUT_URL = reverse("account:logout")
TOKEN_URL = reverse("account:token")
ME_USER_URL = reverse("account:me")


def create_user(phone, password=None):
    """Helper Function For Create User"""
    return get_user_model().objects.create_user(phone=phone, password=password)


class PublicTests(TestCase):
    """Test Cases which doesn't require authentication"""

    def setUp(self):
        self.client = APIClient()

    def test_register_should_work_properly(self):
        """Test User Registeration"""
        payload = {
            "phone": "09151498722",
        }

        res = self.client.post(AUTH_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # is_user_exist = get_user_model().objects.filter(phone=payload["phone"]).exists()
        # self.assertTrue(is_user_exist)

    def test_login_should_work_properly(self):
        """Test User Login"""
        payload = {
            "phone": "09151498722",
        }
        user = create_user(payload["phone"], password="123456")
        old_password = user.password

        res = self.client.post(AUTH_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # def test_create_token_should_work_properly(self):
    #     """Test For Creation The Token"""
    #     payload = {"phone": "09151498722", "password": "123456"}

    #     create_user(payload["phone"], payload["password"])

    #     res = self.client.post(TOKEN_URL, payload)

    #     # self.assertIn("access", res.data)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateTest(TestCase):
    """Test APIs Which Needs User To Be Authenticated"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user("09151498722")

        self.client.force_authenticate(self.user)

    def test_retrieve_user_profile(self):
        """Test Retrieve User With His Token"""
        res = self.client.get(ME_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["phone"], self.user.phone)

    def test_update_user_profile(self):
        """Test Update User Profile"""
        payload = {"fullName": "NewHamid"}

        res = self.client.patch(ME_USER_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.fullName, payload["fullName"])

    # def test_logout_user(self):
    #     """Test Logout User"""
    #     res = self.client.get(LOGOUT_URL)

    #     self.assertNotIn(self.user, res.request)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
