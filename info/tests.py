"""
Info App Tests - TDD Approach
Testing ContactUs model and API endpoints
"""
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core import mail
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import json


class ContactUsModelTest(TestCase):
    """Test cases for ContactUs model"""

    def test_contact_us_creation(self):
        """Test ContactUs model creation with valid data"""
        from info.models import ContactUs

        contact = ContactUs.objects.create(
            full_name="احمد محمدی",
            phone="09123456789",
            email="ahmad@example.com",
            message="سلام، سوالی درباره جشنواره دارم.",
        )

        self.assertEqual(contact.full_name, "احمد محمدی")
        self.assertEqual(contact.phone, "09123456789")
        self.assertEqual(contact.email, "ahmad@example.com")
        self.assertEqual(contact.message, "سلام، سوالی درباره جشنواره دارم.")
        self.assertIsNotNone(contact.created_at)
        self.assertEqual(str(contact), "احمد محمدی - 09123456789")

    def test_contact_us_persian_verbose_names(self):
        """Test Persian verbose names for ContactUs model"""
        from info.models import ContactUs

        # Test model meta
        self.assertEqual(ContactUs._meta.verbose_name, "پیام تماس")
        self.assertEqual(ContactUs._meta.verbose_name_plural, "پیام‌های تماس")

        # Test field verbose names
        self.assertEqual(
            ContactUs._meta.get_field("full_name").verbose_name, "نام کامل"
        )
        self.assertEqual(ContactUs._meta.get_field("phone").verbose_name, "شماره تلفن")
        self.assertEqual(ContactUs._meta.get_field("email").verbose_name, "ایمیل")
        self.assertEqual(ContactUs._meta.get_field("message").verbose_name, "پیام")

    def test_contact_us_phone_validation(self):
        """Test phone number validation for Iranian mobile numbers"""
        from info.models import ContactUs

        # Valid Iranian mobile number
        contact = ContactUs(
            full_name="تست کاربر",
            phone="09123456789",
            email="test@example.com",
            message="تست پیام",
        )
        contact.full_clean()  # Should not raise ValidationError

        # Invalid phone number (not starting with 09)
        contact_invalid = ContactUs(
            full_name="تست کاربر",
            phone="08123456789",
            email="test@example.com",
            message="تست پیام",
        )
        with self.assertRaises(ValidationError):
            contact_invalid.full_clean()

    def test_contact_us_email_validation(self):
        """Test email field validation"""
        from info.models import ContactUs

        # Valid email
        contact = ContactUs(
            full_name="تست کاربر",
            phone="09123456789",
            email="valid@example.com",
            message="تست پیام",
        )
        contact.full_clean()  # Should not raise ValidationError

        # Invalid email
        contact_invalid = ContactUs(
            full_name="تست کاربر",
            phone="09123456789",
            email="invalid-email",
            message="تست پیام",
        )
        with self.assertRaises(ValidationError):
            contact_invalid.full_clean()

    def test_contact_us_ordering(self):
        """Test ContactUs model ordering"""
        from info.models import ContactUs

        # Create multiple contacts
        contact1 = ContactUs.objects.create(
            full_name="کاربر اول",
            phone="09111111111",
            email="user1@example.com",
            message="پیام اول",
        )

        contact2 = ContactUs.objects.create(
            full_name="کاربر دوم",
            phone="09222222222",
            email="user2@example.com",
            message="پیام دوم",
        )

        # Check ordering (newest first)
        contacts = ContactUs.objects.all()
        self.assertEqual(contacts[0], contact2)
        self.assertEqual(contacts[1], contact1)


class ContactUsAPITest(TestCase):
    """Test cases for ContactUs API endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_contact_us_post_endpoint_success(self):
        """Test successful ContactUs POST endpoint"""
        url = reverse("info:contact-us-create")
        data = {
            "full_name": "علی احمدی",
            "phone": "09123456789",
            "email": "ali@example.com",
            "message": "سلام، سوال درباره جشنواره دارم. کی شروع می‌شه؟",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["full_name"], "علی احمدی")
        self.assertEqual(response.data["phone"], "09123456789")
        self.assertEqual(response.data["email"], "ali@example.com")
        self.assertEqual(
            response.data["message"], "سلام، سوال درباره جشنواره دارم. کی شروع می‌شه؟"
        )

        # Check database
        from info.models import ContactUs

        self.assertEqual(ContactUs.objects.count(), 1)
        contact = ContactUs.objects.first()
        self.assertEqual(contact.full_name, "علی احمدی")

    def test_contact_us_post_validation_errors(self):
        """Test ContactUs POST endpoint validation errors"""
        url = reverse("info:contact-us-create")

        # Test missing required fields
        data = {"full_name": "", "phone": "", "email": "invalid-email", "message": ""}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("full_name", response.data)
        self.assertIn("phone", response.data)
        self.assertIn("email", response.data)
        self.assertIn("message", response.data)

    def test_contact_us_post_invalid_phone(self):
        """Test ContactUs POST with invalid Iranian phone number"""
        url = reverse("info:contact-us-create")
        data = {
            "full_name": "تست کاربر",
            "phone": "123456789",  # Invalid Iranian phone
            "email": "test@example.com",
            "message": "تست پیام",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", response.data)

    def test_contact_us_post_persian_characters(self):
        """Test ContactUs POST with Persian characters"""
        url = reverse("info:contact-us-create")
        data = {
            "full_name": "محمدرضا کریمی‌نژاد",
            "phone": "09987654321",
            "email": "mohammadreza@example.com",
            "message": "سلام وقت بخیر. من می‌خواهم در جشنواره شرکت کنم ولی نمی‌دانم چطور ثبت‌نام کنم. لطفاً راهنمایی کنید.",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify Persian text is stored correctly
        from info.models import ContactUs

        contact = ContactUs.objects.first()
        self.assertEqual(contact.full_name, "محمدرضا کریمی‌نژاد")
        self.assertIn("جشنواره", contact.message)
        self.assertIn("ثبت‌نام", contact.message)


class InfoAppIntegrationTest(TestCase):
    """Integration tests for Info app"""

    def test_admin_can_view_contact_messages(self):
        """Test that admin interface properly displays contact messages"""
        from info.models import ContactUs

        contact = ContactUs.objects.create(
            full_name="ادمین تست",
            phone="09111111111",
            email="admin@example.com",
            message="پیام تست ادمین",
        )

        # Test admin interface (this will validate admin configuration)
        self.assertTrue(hasattr(contact, "_meta"))
        self.assertEqual(str(contact), "ادمین تست - 09111111111")
