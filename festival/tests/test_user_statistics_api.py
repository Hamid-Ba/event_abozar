"""
Tests for Authenticated User Statistics API
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

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


class AuthenticatedUserStatisticsAPITest(APITestCase):
    """Test cases for Authenticated User Statistics API endpoint"""

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

        # Create festival registrations for user1
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
            user=self.user1,  # Same user, different registration
            full_name="علی احمدی",
            father_name="حسین",
            national_id="1234567891",
            gender="male",
            education="کارشناسی ارشد",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست۲",
            festival_format=self.format_interview,
            festival_topic=self.topic_jihad,
        )

        # Create festival registration for user2
        self.registration3 = FestivalRegistration.objects.create(
            user=self.user2,
            full_name="فاطمه حسینی",
            father_name="محمد",
            national_id="1234567892",
            gender="female",
            education="کارشناسی",
            phone_number="09123456790",
            province=self.province,
            city=self.city,
            media_name="رسانه تست۳",
            festival_format=self.format_doc,
            festival_topic=FestivalTopic.objects.get(code="family_society"),
        )

        # Create some works for user1
        # Create a temporary file for testing
        test_file1 = SimpleUploadedFile(
            "test_work1.txt", b"Test content for work 1", content_type="text/plain"
        )
        self.work1 = Work.objects.create(
            festival_registration=self.registration1,
            title="اثر تست ۱",
            description="توضیحات اثر تست ۱",
            file=test_file1,
        )

        test_file2 = SimpleUploadedFile(
            "test_work2.txt", b"Test content for work 2", content_type="text/plain"
        )
        self.work2 = Work.objects.create(
            festival_registration=self.registration2,
            title="اثر تست ۲",
            description="توضیحات اثر تست ۲",
            file=test_file2,
        )

        # Create work for user2
        test_file3 = SimpleUploadedFile(
            "test_work3.txt", b"Test content for work 3", content_type="text/plain"
        )
        self.work3 = Work.objects.create(
            festival_registration=self.registration3,
            title="اثر تست ۳",
            description="توضیحات اثر تست ۳",
            file=test_file3,
        )

        # Create some content (events, education, news) for total count
        Event.objects.create(title="رویداد تست ۱", description="توضیحات رویداد تست")

        Education.objects.create(title="آموزش تست ۱", description="توضیحات آموزش تست")

        News.objects.create(title="خبر تست ۱", description="توضیحات خبر تست")

    def test_my_statistics_unauthenticated(self):
        """Test my statistics access for unauthenticated users should be forbidden"""
        url = reverse("festival:my-statistics")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_statistics_authenticated_success(self):
        """Test successful my statistics retrieval for authenticated user"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:my-statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User1 has 2 registrations, 2 works, and total content count should be 3
        self.assertEqual(response.data["my_registrations_count"], 2)
        self.assertEqual(response.data["my_works_count"], 2)
        self.assertEqual(response.data["total_content_count"], 3)

    def test_my_statistics_different_user(self):
        """Test my statistics for different user shows their own data"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("festival:my-statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User2 has 1 registration, 1 work, and total content count should be 3
        self.assertEqual(response.data["my_registrations_count"], 1)
        self.assertEqual(response.data["my_works_count"], 1)
        self.assertEqual(response.data["total_content_count"], 3)

    def test_my_statistics_structure(self):
        """Test that my statistics response has correct structure"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:my-statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("my_registrations_count", response.data)
        self.assertIn("my_works_count", response.data)
        self.assertIn("total_content_count", response.data)

    def test_my_statistics_user_with_no_data(self):
        """Test my statistics for user with no registrations or works"""
        user_no_data = User.objects.create(
            phone="09123456799", fullName="کاربر بدون داده"
        )
        self.client.force_authenticate(user=user_no_data)
        url = reverse("festival:my-statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["my_registrations_count"], 0)
        self.assertEqual(response.data["my_works_count"], 0)
        self.assertEqual(
            response.data["total_content_count"], 3
        )  # Still shows total content

    def test_my_statistics_response_format(self):
        """Test that my statistics response format is correct"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:my-statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check data types
        self.assertIsInstance(response.data["my_registrations_count"], int)
        self.assertIsInstance(response.data["my_works_count"], int)
        self.assertIsInstance(response.data["total_content_count"], int)

        # Check non-negative values
        self.assertGreaterEqual(response.data["my_registrations_count"], 0)
        self.assertGreaterEqual(response.data["my_works_count"], 0)
        self.assertGreaterEqual(response.data["total_content_count"], 0)

    def test_my_statistics_with_additional_content(self):
        """Test that total content count updates when new content is added"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:my-statistics")

        # Get initial count
        response1 = self.client.get(url)
        initial_content_count = response1.data["total_content_count"]

        # Add new content
        Event.objects.create(title="رویداد جدید", description="توضیحات رویداد جدید")

        # Get updated count
        response2 = self.client.get(url)
        updated_content_count = response2.data["total_content_count"]

        # Should be incremented by 1
        self.assertEqual(updated_content_count, initial_content_count + 1)

        # User's personal data should remain the same
        self.assertEqual(response2.data["my_registrations_count"], 2)
        self.assertEqual(response2.data["my_works_count"], 2)

    def test_my_statistics_with_new_registration(self):
        """Test that user's registration count updates when they add new registration"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:my-statistics")

        # Get initial count
        response1 = self.client.get(url)
        initial_registrations_count = response1.data["my_registrations_count"]

        # Add new registration for user1
        FestivalRegistration.objects.create(
            user=self.user1,
            full_name="علی احمدی",
            father_name="حسین",
            national_id="1234567893",
            gender="male",
            education="کارشناسی ارشد",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه جدید",
            festival_format=FestivalFormat.objects.get(code="photo"),
            festival_topic=FestivalTopic.objects.get(code="hope_happiness"),
        )

        # Get updated count
        response2 = self.client.get(url)
        updated_registrations_count = response2.data["my_registrations_count"]

        # Should be incremented by 1
        self.assertEqual(updated_registrations_count, initial_registrations_count + 1)

    def test_my_statistics_isolation_between_users(self):
        """Test that users only see their own statistics"""
        # User1's statistics
        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:my-statistics")
        response1 = self.client.get(url)

        user1_registrations = response1.data["my_registrations_count"]
        user1_works = response1.data["my_works_count"]

        # User2's statistics
        self.client.force_authenticate(user=self.user2)
        response2 = self.client.get(url)

        user2_registrations = response2.data["my_registrations_count"]
        user2_works = response2.data["my_works_count"]

        # Should be different
        self.assertNotEqual(user1_registrations, user2_registrations)
        self.assertNotEqual(user1_works, user2_works)

        # But total content should be same for both
        self.assertEqual(
            response1.data["total_content_count"], response2.data["total_content_count"]
        )
