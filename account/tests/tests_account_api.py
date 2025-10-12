"""
Tests Account Module APIs
"""
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

REGISTER_URL = reverse("account:register")
LOGIN_URL = reverse("account:login")
ME_USER_URL = reverse("account:me")


def create_user(phone, password=None):
    """Helper Function For Create User"""
    return get_user_model().objects.create_user(phone=phone, password=password)


class PublicTests(TestCase):
    """Test Cases which doesn't require authentication"""

    def setUp(self):
        self.client = APIClient()

    def test_register_new_user_should_work(self):
        """Test User Registration with new user"""
        payload = {
            "full_name": "احمد محمدی",
            "phone": "09151498722",
            "password": "123456",
        }

        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Check user was created
        user_exists = get_user_model().objects.filter(phone=payload["phone"]).exists()
        self.assertTrue(user_exists)

        # Check response data
        self.assertIn("message", res.data)
        self.assertIn("user", res.data)
        self.assertEqual(res.data["user"]["phone"], payload["phone"])
        self.assertEqual(res.data["user"]["full_name"], payload["full_name"])

    def test_register_existing_user_updates_password_only(self):
        """Test User Registration with existing user updates password but keeps original fullName"""
        # Create existing user first
        existing_user = create_user("09151498722", password="oldpassword")
        existing_user.fullName = "Original Name"
        existing_user.save()

        payload = {
            "full_name": "New Name (should be ignored)",
            "phone": "09151498722",
            "password": "newpassword",
        }

        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Check password was updated but fullName was NOT changed
        existing_user.refresh_from_db()
        self.assertEqual(
            existing_user.fullName, "Original Name"
        )  # Should keep original name
        self.assertTrue(
            existing_user.check_password(payload["password"])
        )  # Password should be updated

        # Check message indicates update
        self.assertIn("به‌روزرسانی", res.data["message"])

        # Check response returns original fullName, not the submitted one
        self.assertEqual(res.data["user"]["full_name"], "Original Name")

    def test_register_with_invalid_phone(self):
        """Test registration with invalid phone number"""
        payload = {
            "full_name": "احمد محمدی",
            "phone": "123456789",  # Invalid phone
            "password": "123456",
        }

        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", res.data)

    def test_login_should_work_properly(self):
        """Test User Login with correct credentials"""
        # Create user first
        user = create_user("09151498722", password="123456")
        user.fullName = "احمد محمدی"
        user.save()

        payload = {"phone": "09151498722", "password": "123456"}

        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check response contains tokens and user info
        self.assertIn("tokens", res.data)
        self.assertIn("access", res.data["tokens"])
        self.assertIn("refresh", res.data["tokens"])
        self.assertIn("user", res.data)
        self.assertEqual(res.data["user"]["phone"], payload["phone"])

    def test_login_with_wrong_password(self):
        """Test login with wrong password"""
        # Create user first
        create_user("09151498722", password="123456")

        payload = {"phone": "09151498722", "password": "wrongpassword"}

        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)

    def test_login_with_nonexistent_user(self):
        """Test login with user that doesn't exist"""
        payload = {"phone": "09999999999", "password": "123456"}

        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)


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
