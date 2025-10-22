"""
Tests for Festival Category List APIs
تست‌های API لیست دسته‌بندی‌های جشنواره
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from festival.models import FestivalFormat, FestivalTopic, FestivalSpecialSection


class FestivalFormatListAPITest(TestCase):
    """Test suite for Festival Format List API"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.url = reverse("festival:format-list")

        # Create test formats
        self.format1 = FestivalFormat.objects.create(
            code="test_format_1",
            name="گزارش خبری",
            description="گزارش‌های خبری",
            is_active=True,
            display_order=1,
        )
        self.format2 = FestivalFormat.objects.create(
            code="test_format_2",
            name="مصاحبه",
            description="مصاحبه‌ها",
            is_active=True,
            display_order=2,
        )
        self.format3 = FestivalFormat.objects.create(
            code="test_format_3",
            name="مستند",
            description="مستندات",
            is_active=False,
            display_order=3,
        )

    def test_list_active_formats_default(self):
        """Test listing only active formats by default"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should only return active formats
        data = response.json()
        self.assertGreaterEqual(len(data), 2)  # At least our 2 active test formats

        # Check that our test formats are in the response
        codes = [item["code"] for item in data]
        self.assertIn("test_format_1", codes)
        self.assertIn("test_format_2", codes)
        self.assertNotIn("test_format_3", codes)  # Inactive should not be included

    def test_list_all_formats(self):
        """Test listing all formats including inactive"""
        response = self.client.get(self.url, {"is_active": "all"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Should include all formats
        codes = [item["code"] for item in data]
        self.assertIn("test_format_1", codes)
        self.assertIn("test_format_2", codes)
        self.assertIn("test_format_3", codes)

    def test_list_inactive_formats_only(self):
        """Test listing only inactive formats"""
        response = self.client.get(self.url, {"is_active": "false"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Filter our test formats
        test_codes = [item["code"] for item in data if item["code"].startswith("test_")]
        self.assertIn("test_format_3", test_codes)
        self.assertNotIn("test_format_1", test_codes)

    def test_format_ordering(self):
        """Test that formats are ordered by display_order and name"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Get our test formats from response
        test_formats = [item for item in data if item["code"].startswith("test_")]

        # Should be ordered by display_order
        self.assertEqual(test_formats[0]["code"], "test_format_1")
        self.assertEqual(test_formats[1]["code"], "test_format_2")

    def test_format_response_structure(self):
        """Test that format response has correct structure"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Find one of our test formats
        test_format = next(
            (item for item in data if item["code"] == "test_format_1"), None
        )
        self.assertIsNotNone(test_format)

        # Check structure
        self.assertIn("id", test_format)
        self.assertIn("code", test_format)
        self.assertIn("name", test_format)
        self.assertIn("description", test_format)

        # Verify values
        self.assertEqual(test_format["name"], "گزارش خبری")
        self.assertEqual(test_format["description"], "گزارش‌های خبری")

    def test_unauthenticated_access_allowed(self):
        """Test that unauthenticated users can access format list"""
        response = self.client.get(self.url)

        # Should succeed without authentication
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FestivalTopicListAPITest(TestCase):
    """Test suite for Festival Topic List API"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.url = reverse("festival:topic-list")

        # Create test topics
        self.topic1 = FestivalTopic.objects.create(
            code="test_topic_1",
            name="شعار سال",
            description="محور شعار سال",
            is_active=True,
            display_order=1,
        )
        self.topic2 = FestivalTopic.objects.create(
            code="test_topic_2",
            name="جهاد تبیین",
            description="محور جهاد تبیین",
            is_active=True,
            display_order=2,
        )
        self.topic3 = FestivalTopic.objects.create(
            code="test_topic_3",
            name="غیرفعال",
            description="محور غیرفعال",
            is_active=False,
            display_order=3,
        )

    def test_list_active_topics_default(self):
        """Test listing only active topics by default"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Check that our test topics are in the response
        codes = [item["code"] for item in data]
        self.assertIn("test_topic_1", codes)
        self.assertIn("test_topic_2", codes)
        self.assertNotIn("test_topic_3", codes)

    def test_topic_response_structure(self):
        """Test that topic response has correct structure"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Find one of our test topics
        test_topic = next(
            (item for item in data if item["code"] == "test_topic_1"), None
        )
        self.assertIsNotNone(test_topic)

        # Check structure
        self.assertIn("id", test_topic)
        self.assertIn("code", test_topic)
        self.assertIn("name", test_topic)
        self.assertIn("description", test_topic)

        # Verify values
        self.assertEqual(test_topic["name"], "شعار سال")
        self.assertEqual(test_topic["description"], "محور شعار سال")

    def test_topic_ordering(self):
        """Test that topics are ordered correctly"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Get our test topics from response
        test_topics = [item for item in data if item["code"].startswith("test_")]

        # Should be ordered by display_order
        self.assertEqual(test_topics[0]["code"], "test_topic_1")
        self.assertEqual(test_topics[1]["code"], "test_topic_2")

    def test_filter_inactive_topics(self):
        """Test filtering inactive topics"""
        response = self.client.get(self.url, {"is_active": "false"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Filter our test topics
        test_codes = [item["code"] for item in data if item["code"].startswith("test_")]
        self.assertIn("test_topic_3", test_codes)


class FestivalSpecialSectionListAPITest(TestCase):
    """Test suite for Festival Special Section List API"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.url = reverse("festival:special-section-list")

        # Create test sections
        self.section1 = FestivalSpecialSection.objects.create(
            code="test_section_1",
            name="روایت پیشرفت",
            description="بخش ویژه روایت پیشرفت",
            is_active=True,
            display_order=1,
        )
        self.section2 = FestivalSpecialSection.objects.create(
            code="test_section_2",
            name="روایت میدان",
            description="بخش ویژه روایت میدان",
            is_active=True,
            display_order=2,
        )
        self.section3 = FestivalSpecialSection.objects.create(
            code="test_section_3",
            name="غیرفعال",
            description="بخش غیرفعال",
            is_active=False,
            display_order=3,
        )

    def test_list_active_sections_default(self):
        """Test listing only active sections by default"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Check that our test sections are in the response
        codes = [item["code"] for item in data]
        self.assertIn("test_section_1", codes)
        self.assertIn("test_section_2", codes)
        self.assertNotIn("test_section_3", codes)

    def test_section_response_structure(self):
        """Test that section response has correct structure"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Find one of our test sections
        test_section = next(
            (item for item in data if item["code"] == "test_section_1"), None
        )
        self.assertIsNotNone(test_section)

        # Check structure
        self.assertIn("id", test_section)
        self.assertIn("code", test_section)
        self.assertIn("name", test_section)
        self.assertIn("description", test_section)

        # Verify values
        self.assertEqual(test_section["name"], "روایت پیشرفت")
        self.assertEqual(test_section["description"], "بخش ویژه روایت پیشرفت")

    def test_section_ordering(self):
        """Test that sections are ordered correctly"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Get our test sections from response
        test_sections = [item for item in data if item["code"].startswith("test_")]

        # Should be ordered by display_order
        self.assertEqual(test_sections[0]["code"], "test_section_1")
        self.assertEqual(test_sections[1]["code"], "test_section_2")

    def test_empty_result_for_no_active_sections(self):
        """Test that API handles case with no active sections"""
        # Deactivate all test sections
        FestivalSpecialSection.objects.filter(code__startswith="test_").update(
            is_active=False
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Should not contain any test sections
        test_codes = [item["code"] for item in data if item["code"].startswith("test_")]
        self.assertEqual(len(test_codes), 0)

    def test_unauthenticated_access_allowed(self):
        """Test that unauthenticated users can access section list"""
        response = self.client.get(self.url)

        # Should succeed without authentication
        self.assertEqual(response.status_code, status.HTTP_200_OK)
