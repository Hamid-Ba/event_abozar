"""
Content API Tests - TDD Approach
Testing API endpoints for News, Education, and Event models
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from account.models import User
from content.models import News, Education, Event


class BaseContentAPITestCase(TestCase):
    """Base test case for content API tests"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create test user
        self.user = User.objects.create_user(phone="09123456789", fullName="تست کاربر")

        # Test image file
        self.test_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"fake image content",
            content_type="image/jpeg",
        )


class NewsAPITest(BaseContentAPITestCase):
    """Test cases for News API endpoints"""

    def setUp(self):
        super().setUp()

        # Create test news
        self.news1 = News.objects.create(
            title="اخبار اول",
            description="توضیحات اخبار اول",
            publish_date=timezone.now().date(),
        )
        self.news1.tags.add("اخبار", "جشنواره")

        self.news2 = News.objects.create(
            title="اخبار دوم",
            description="توضیحات اخبار دوم",
            publish_date=timezone.now().date(),
        )
        self.news2.tags.add("رسانه")

    def test_news_list_api(self):
        """Test news list endpoint"""
        url = reverse("content:news-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)

        # Check pagination structure (matching StandardPagination)
        self.assertIn("total_items", response.data)
        self.assertIn("total_pages", response.data)
        self.assertIn("current_page", response.data)
        self.assertIn("links", response.data)

    def test_news_detail_api(self):
        """Test news detail endpoint"""
        url = reverse("content:news-detail", kwargs={"pk": self.news1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "اخبار اول")
        self.assertEqual(response.data["description"], "توضیحات اخبار اول")
        self.assertIn("اخبار", response.data["tags"])
        self.assertIn("جشنواره", response.data["tags"])

    def test_news_search(self):
        """Test news search functionality"""
        url = reverse("content:news-list")
        response = self.client.get(url, {"search": "اول"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "اخبار اول")

    def test_news_filter_by_tag(self):
        """Test news filtering by tag"""
        url = reverse("content:news-list")
        response = self.client.get(url, {"tags__name": "رسانه"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "اخبار دوم")

    def test_news_ordering(self):
        """Test news ordering"""
        url = reverse("content:news-list")
        response = self.client.get(url, {"ordering": "title"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [item["title"] for item in response.data["results"]]
        self.assertEqual(titles, sorted(titles))

    def test_news_detail_not_found(self):
        """Test news detail with non-existent ID"""
        url = reverse("content:news-detail", kwargs={"pk": 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class EducationAPITest(BaseContentAPITestCase):
    """Test cases for Education API endpoints"""

    def setUp(self):
        super().setUp()

        # Create test education content
        self.education1 = Education.objects.create(
            title="آموزش اول",
            description="توضیحات آموزش اول",
            publish_date=timezone.now().date(),
        )
        self.education1.tags.add("آموزش", "رسانه")

        self.education2 = Education.objects.create(
            title="آموزش دوم",
            description="توضیحات آموزش دوم",
            publish_date=timezone.now().date(),
        )
        self.education2.tags.add("فیلمسازی")

    def test_education_list_api(self):
        """Test education list endpoint"""
        url = reverse("content:education-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)

    def test_education_detail_api(self):
        """Test education detail endpoint"""
        url = reverse("content:education-detail", kwargs={"pk": self.education1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "آموزش اول")
        self.assertEqual(response.data["description"], "توضیحات آموزش اول")
        self.assertIn("آموزش", response.data["tags"])
        self.assertIn("رسانه", response.data["tags"])

    def test_education_search(self):
        """Test education search functionality"""
        url = reverse("content:education-list")
        response = self.client.get(url, {"search": "دوم"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "آموزش دوم")

    def test_education_filter_by_tag(self):
        """Test education filtering by tag"""
        url = reverse("content:education-list")
        response = self.client.get(url, {"tags__name": "فیلمسازی"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "آموزش دوم")


class EventAPITest(BaseContentAPITestCase):
    """Test cases for Event API endpoints"""

    def setUp(self):
        super().setUp()

        # Create test events
        self.event1 = Event.objects.create(
            title="رویداد اول",
            description="توضیحات رویداد اول",
            publish_date=timezone.now().date(),
        )
        self.event1.tags.add("رویداد", "جشنواره")

        self.event2 = Event.objects.create(
            title="رویداد دوم",
            description="توضیحات رویداد دوم",
            publish_date=timezone.now().date(),
        )
        self.event2.tags.add("مراسم")

    def test_event_list_api(self):
        """Test event list endpoint"""
        url = reverse("content:event-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)

    def test_event_detail_api(self):
        """Test event detail endpoint"""
        url = reverse("content:event-detail", kwargs={"pk": self.event1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "رویداد اول")
        self.assertEqual(response.data["description"], "توضیحات رویداد اول")
        self.assertIn("رویداد", response.data["tags"])
        self.assertIn("جشنواره", response.data["tags"])

    def test_event_search(self):
        """Test event search functionality"""
        url = reverse("content:event-list")
        response = self.client.get(url, {"search": "اول"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "رویداد اول")

    def test_event_filter_by_tag(self):
        """Test event filtering by tag"""
        url = reverse("content:event-list")
        response = self.client.get(url, {"tags__name": "مراسم"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "رویداد دوم")


class ContentAPIIntegrationTest(BaseContentAPITestCase):
    """Integration tests for content API"""

    def setUp(self):
        super().setUp()

        # Create content across all models
        News.objects.create(
            title="اخبار تست", description="توضیحات", publish_date=timezone.now().date()
        )
        Education.objects.create(
            title="آموزش تست", description="توضیحات", publish_date=timezone.now().date()
        )
        Event.objects.create(
            title="رویداد تست",
            description="توضیحات",
            publish_date=timezone.now().date(),
        )

    def test_all_endpoints_accessible(self):
        """Test that all content endpoints are accessible"""
        endpoints = [
            "content:news-list",
            "content:education-list",
            "content:event-list",
        ]

        for endpoint in endpoints:
            url = reverse(endpoint)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pagination_consistency(self):
        """Test that pagination works consistently across all endpoints"""
        endpoints = [
            "content:news-list",
            "content:education-list",
            "content:event-list",
        ]

        for endpoint in endpoints:
            url = reverse(endpoint)
            response = self.client.get(url)

            # Check pagination structure (matching StandardPagination)
            self.assertIn("total_items", response.data)
            self.assertIn("total_pages", response.data)
            self.assertIn("current_page", response.data)
            self.assertIn("links", response.data)
            self.assertIn("results", response.data)

    def test_authenticated_vs_anonymous_access(self):
        """Test that both authenticated and anonymous users can access content"""
        url = reverse("content:news-list")

        # Anonymous access
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Authenticated access
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
