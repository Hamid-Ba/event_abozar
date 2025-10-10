"""
Test account module models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class UserTest(TestCase):
    """User Model Tests"""

    def test_create_user_should_work_properly(self):
        """Test Creating a Nromal User"""
        phone = "09151498722"
        password = "password123456"

        user = get_user_model().objects.create_user(phone=phone, password=password)

        self.assertEqual(user.phone, phone)
        self.assertTrue(user.check_password(password))

    def test_phone_is_required(self):
        """user phone is required"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(phone="")

    def test_create_superuser_work_properly(self):
        """Test Create Super User"""
        phone = "09151498722"
        password = "password123456"

        user = get_user_model().objects.create_superuser(phone=phone, password=password)

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.phone, phone)
        self.assertTrue(user.check_password(password))
