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

    def test_education_list_includes_media_fields(self):
        """Test that education list includes video and document fields"""
        url = reverse("content:education-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_item = response.data["results"][0]

        # Check that media fields are present
        self.assertIn("has_video", first_item)
        self.assertIn("has_document", first_item)
        self.assertIn("video_url", first_item)
        self.assertIn("document_url", first_item)

        # Initially should be False/None
        self.assertFalse(first_item["has_video"])
        self.assertFalse(first_item["has_document"])
        self.assertIsNone(first_item["video_url"])
        self.assertIsNone(first_item["document_url"])

    def test_education_detail_includes_media_fields(self):
        """Test that education detail includes video and document fields"""
        url = reverse("content:education-detail", kwargs={"pk": self.education1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that media fields are present
        self.assertIn("video", response.data)
        self.assertIn("document", response.data)

    def test_education_with_video_file(self):
        """Test education with uploaded video file"""
        # Create education with video
        mock_video = SimpleUploadedFile(
            "tutorial.mp4", b"fake video content", content_type="video/mp4"
        )

        education = Education.objects.create(
            title="آموزش ویدیویی",
            description="آموزش با ویدیو",
            publish_date=timezone.now().date(),
            video=mock_video,
        )

        # Test list endpoint
        url = reverse("content:education-list")
        response = self.client.get(url)

        # Find our education in results
        edu_data = next(
            (item for item in response.data["results"] if item["id"] == education.id),
            None,
        )

        self.assertIsNotNone(edu_data)
        self.assertTrue(edu_data["has_video"])
        self.assertIsNotNone(edu_data["video_url"])
        # Check URL contains the correct extension (filename is random UUID)
        self.assertTrue(edu_data["video_url"].endswith(".mp4"))

        # Test detail endpoint
        detail_url = reverse("content:education-detail", kwargs={"pk": education.pk})
        detail_response = self.client.get(detail_url)

        self.assertIsNotNone(detail_response.data["video"])

    def test_education_with_document_file(self):
        """Test education with uploaded document file"""
        # Create education with document
        mock_document = SimpleUploadedFile(
            "slides.pdf", b"fake pdf content", content_type="application/pdf"
        )

        education = Education.objects.create(
            title="آموزش با اسناد",
            description="آموزش با فایل PDF",
            publish_date=timezone.now().date(),
            document=mock_document,
        )

        # Test list endpoint
        url = reverse("content:education-list")
        response = self.client.get(url)

        # Find our education in results
        edu_data = next(
            (item for item in response.data["results"] if item["id"] == education.id),
            None,
        )

        self.assertIsNotNone(edu_data)
        self.assertTrue(edu_data["has_document"])
        self.assertIsNotNone(edu_data["document_url"])
        # Check URL contains the correct extension (filename is random UUID)
        self.assertTrue(edu_data["document_url"].endswith(".pdf"))

        # Test detail endpoint
        detail_url = reverse("content:education-detail", kwargs={"pk": education.pk})
        detail_response = self.client.get(detail_url)

        self.assertIsNotNone(detail_response.data["document"])

    def test_education_with_both_video_and_document(self):
        """Test education with both video and document files"""
        mock_video = SimpleUploadedFile(
            "course.mp4", b"fake video content", content_type="video/mp4"
        )
        mock_document = SimpleUploadedFile(
            "materials.pptx",
            b"fake pptx content",
            content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )

        education = Education.objects.create(
            title="دوره کامل",
            description="دوره با ویدیو و اسناد",
            publish_date=timezone.now().date(),
            video=mock_video,
            document=mock_document,
        )

        # Test list endpoint
        url = reverse("content:education-list")
        response = self.client.get(url)

        edu_data = next(
            (item for item in response.data["results"] if item["id"] == education.id),
            None,
        )

        self.assertIsNotNone(edu_data)
        self.assertTrue(edu_data["has_video"])
        self.assertTrue(edu_data["has_document"])
        self.assertIsNotNone(edu_data["video_url"])
        self.assertIsNotNone(edu_data["document_url"])


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
