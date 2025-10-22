"""
Tests for Statistics API
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from festival.models import (
    FestivalRegistration,
    FestivalFormat,
    FestivalTopic,
    FestivalSpecialSection,
    Work,
)
from content.models import Event, Education, News
from province.models import Province, City

User = get_user_model()


class StatisticsAPITest(APITestCase):
    """Test cases for Statistics API endpoint"""

    def setUp(self):
        """Set up test data"""
        # Create test provinces and cities
        self.province = Province.objects.create(name="تهران", slug="tehran")
        self.city = City.objects.create(
            name="تهران", slug="tehran-city", province=self.province
        )

        # Load category objects
        self.format_news = FestivalFormat.objects.get(code="news_report")
        self.format_interview = FestivalFormat.objects.get(code="interview")
        self.format_doc = FestivalFormat.objects.get(code="documentary")
        self.topic_slogan = FestivalTopic.objects.get(code="year_slogan")
        self.topic_jihad = FestivalTopic.objects.get(code="jihad_explanation")

        # Create test users
        self.user1 = User.objects.create(phone="09123456789", fullName="علی احمدی")
        self.user2 = User.objects.create(phone="09123456790", fullName="فاطمه حسینی")
        self.user3 = User.objects.create(phone="09123456791", fullName="محمد رضایی")

        # Create festival registrations
        self.registration1 = FestivalRegistration.objects.create(
            user=self.user1,
            full_name="علی احمدی",
            father_name="حسین",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست۱",
            festival_format=self.format_news,
            festival_topic=self.topic_slogan,
        )

        self.registration2 = FestivalRegistration.objects.create(
            user=self.user2,
            full_name="فاطمه حسینی",
            father_name="محمد",
            national_id="1234567891",
            gender="female",
            education="کارشناسی ارشد",
            phone_number="09123456790",
            province=self.province,
            city=self.city,
            media_name="رسانه تست۲",
            festival_format=self.format_interview,
            festival_topic=self.topic_jihad,
        )

        # Create works (note: file field is required but we'll handle it in tests)
        # We'll need to create temporary files or mock this

    def test_statistics_endpoint_no_authentication_required(self):
        """Test that statistics endpoint doesn't require authentication"""
        url = reverse("festival:statistics")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_statistics_structure(self):
        """Test that statistics response has correct structure"""
        url = reverse("festival:statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("registered_users_count", response.data)
        self.assertIn("total_works_count", response.data)
        self.assertIn("content_count", response.data)

    def test_registered_users_count(self):
        """Test that registered users count is correct"""
        url = reverse("festival:statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # We created 2 festival registrations
        self.assertEqual(response.data["registered_users_count"], 2)

    def test_registered_users_count_empty(self):
        """Test registered users count when no registrations exist"""
        # Delete all registrations
        FestivalRegistration.objects.all().delete()

        url = reverse("festival:statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["registered_users_count"], 0)

    def test_total_works_count_empty(self):
        """Test works count when no works exist"""
        url = reverse("festival:statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # No works created in setUp
        self.assertEqual(response.data["total_works_count"], 0)

    def test_content_count_empty(self):
        """Test content count when no content exists"""
        url = reverse("festival:statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # No content created in setUp
        self.assertEqual(response.data["content_count"], 0)

    def test_content_count_with_mixed_content(self):
        """Test content count with events, education, and news"""
        # Create test content
        Event.objects.create(title="رویداد تست ۱", description="توضیحات رویداد تست")

        Event.objects.create(title="رویداد تست ۲", description="توضیحات رویداد تست")

        Education.objects.create(title="آموزش تست ۱", description="توضیحات آموزش تست")

        News.objects.create(title="خبر تست ۱", description="توضیحات خبر تست")

        News.objects.create(title="خبر تست ۲", description="توضیحات خبر تست")

        url = reverse("festival:statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should count 2 events + 1 education + 2 news = 5 total
        self.assertEqual(response.data["content_count"], 5)

    def test_content_count_with_single_event(self):
        """Test content count with single event"""
        # Create content
        Event.objects.create(title="رویداد تست", description="توضیحات")

        url = reverse("festival:statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should count the single event (1)
        self.assertEqual(response.data["content_count"], 1)

    def test_statistics_response_format(self):
        """Test that statistics response format is correct"""
        url = reverse("festival:statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check data types
        self.assertIsInstance(response.data["registered_users_count"], int)
        self.assertIsInstance(response.data["total_works_count"], int)
        self.assertIsInstance(response.data["content_count"], int)

        # Check non-negative values
        self.assertGreaterEqual(response.data["registered_users_count"], 0)
        self.assertGreaterEqual(response.data["total_works_count"], 0)
        self.assertGreaterEqual(response.data["content_count"], 0)

    def test_statistics_caching_behavior(self):
        """Test that statistics endpoint returns consistent data on multiple calls"""
        url = reverse("festival:statistics")

        # Make multiple requests
        response1 = self.client.get(url)
        response2 = self.client.get(url)

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Should return same data
        self.assertEqual(response1.data, response2.data)

    def test_statistics_with_additional_registrations(self):
        """Test statistics count updates when new registrations are added"""
        url = reverse("festival:statistics")

        # Get initial count
        response1 = self.client.get(url)
        initial_count = response1.data["registered_users_count"]

        # Add new registration
        FestivalRegistration.objects.create(
            user=self.user3,
            full_name="محمد رضایی",
            father_name="علی",
            national_id="1234567892",
            gender="male",
            education="کارشناسی",
            phone_number="09123456791",
            province=self.province,
            city=self.city,
            media_name="رسانه تست۳",
            festival_format=self.format_doc,
            festival_topic=FestivalTopic.objects.get(code="family_society"),
        )

        # Get updated count
        response2 = self.client.get(url)
        updated_count = response2.data["registered_users_count"]

        # Should be incremented by 1
        self.assertEqual(updated_count, initial_count + 1)
