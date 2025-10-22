"""
Content Models Tests - TDD Approach
Testing News, Education, and Event models
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from taggit.models import Tag
from datetime import datetime, date


class NewsModelTest(TestCase):
    """Test cases for News model"""

    def setUp(self):
        """Set up test data"""
        self.valid_news_data = {
            "title": "اخبار مهم جشنواره",
            "description": "توضیحات کاملی از اخبار جشنواره ابوذر که شامل جزئیات مختلف می‌باشد.",
            "publish_date": timezone.now().date(),
        }

    def test_create_news_success(self):
        """Test creating a valid news item"""
        from content.models import News

        news = News.objects.create(**self.valid_news_data)

        self.assertEqual(news.title, "اخبار مهم جشنواره")
        self.assertEqual(
            news.description,
            "توضیحات کاملی از اخبار جشنواره ابوذر که شامل جزئیات مختلف می‌باشد.",
        )
        self.assertEqual(news.publish_date, self.valid_news_data["publish_date"])
        self.assertTrue(news.created_at)
        self.assertTrue(news.updated_at)

    def test_news_string_representation(self):
        """Test string representation of News"""
        from content.models import News

        news = News.objects.create(**self.valid_news_data)
        self.assertEqual(str(news), "اخبار مهم جشنواره")

    def test_news_required_fields(self):
        """Test that required fields cannot be None"""
        from content.models import News

        # Test missing title
        with self.assertRaises((IntegrityError, ValidationError)):
            news = News(
                title=None, description="توضیحات", publish_date=timezone.now().date()
            )
            news.full_clean()

        # Test missing description
        with self.assertRaises((IntegrityError, ValidationError)):
            news = News(
                title="عنوان", description=None, publish_date=timezone.now().date()
            )
            news.full_clean()

        # Test missing publish_date
        with self.assertRaises((IntegrityError, ValidationError)):
            news = News(title="عنوان", description="توضیحات", publish_date=None)
            news.full_clean()

    def test_news_tags_functionality(self):
        """Test taggit tags functionality"""
        from content.models import News

        news = News.objects.create(**self.valid_news_data)

        # Add tags
        news.tags.add("جشنواره", "اخبار", "رسانه")

        # Test tags were added
        self.assertEqual(news.tags.count(), 3)
        self.assertIn("جشنواره", [tag.name for tag in news.tags.all()])
        self.assertIn("اخبار", [tag.name for tag in news.tags.all()])
        self.assertIn("رسانه", [tag.name for tag in news.tags.all()])

    def test_news_image_field_optional(self):
        """Test that image field is optional"""
        from content.models import News

        news = News.objects.create(**self.valid_news_data)
        self.assertIsNone(news.image.name)  # No image uploaded

    def test_news_ordering(self):
        """Test default ordering by publish date (newest first)"""
        from content.models import News

        # Create news with different dates
        old_news = News.objects.create(
            title="اخبار قدیمی", description="توضیحات", publish_date=date(2024, 1, 1)
        )

        new_news = News.objects.create(
            title="اخبار جدید", description="توضیحات", publish_date=date(2024, 12, 31)
        )

        # Check ordering (newest first)
        news_list = list(News.objects.all())
        self.assertEqual(news_list[0], new_news)
        self.assertEqual(news_list[1], old_news)

    def test_news_meta_options(self):
        """Test model meta options"""
        from content.models import News

        self.assertEqual(News._meta.verbose_name, "خبر")
        self.assertEqual(News._meta.verbose_name_plural, "اخبار")
        self.assertEqual(News._meta.ordering, ["-publish_date"])


class EducationModelTest(TestCase):
    """Test cases for Education model"""

    def setUp(self):
        """Set up test data"""
        self.valid_education_data = {
            "title": "آموزش تولید محتوای رسانه‌ای",
            "description": "دوره‌ای جامع برای آموزش تولید محتوای با کیفیت در حوزه رسانه.",
            "publish_date": timezone.now().date(),
        }

    def test_create_education_success(self):
        """Test creating a valid education item"""
        from content.models import Education

        education = Education.objects.create(**self.valid_education_data)

        self.assertEqual(education.title, "آموزش تولید محتوای رسانه‌ای")
        self.assertEqual(
            education.description,
            "دوره‌ای جامع برای آموزش تولید محتوای با کیفیت در حوزه رسانه.",
        )
        self.assertEqual(
            education.publish_date, self.valid_education_data["publish_date"]
        )

    def test_education_string_representation(self):
        """Test string representation of Education"""
        from content.models import Education

        education = Education.objects.create(**self.valid_education_data)
        self.assertEqual(str(education), "آموزش تولید محتوای رسانه‌ای")

    def test_education_tags_functionality(self):
        """Test taggit tags functionality"""
        from content.models import Education

        education = Education.objects.create(**self.valid_education_data)
        education.tags.add("آموزش", "رسانه", "محتوا")

        self.assertEqual(education.tags.count(), 3)
        self.assertIn("آموزش", [tag.name for tag in education.tags.all()])

    def test_education_meta_options(self):
        """Test model meta options"""
        from content.models import Education

        self.assertEqual(Education._meta.verbose_name, "آموزش")
        self.assertEqual(Education._meta.verbose_name_plural, "آموزش‌ها")
        self.assertEqual(Education._meta.ordering, ["-publish_date"])

    def test_education_video_field_optional(self):
        """Test that video field is optional"""
        from content.models import Education

        education = Education.objects.create(**self.valid_education_data)
        self.assertFalse(education.video)  # No video uploaded
        self.assertFalse(education.has_video)  # has_video property should be False

    def test_education_document_field_optional(self):
        """Test that document field is optional"""
        from content.models import Education

        education = Education.objects.create(**self.valid_education_data)
        self.assertFalse(education.document)  # No document uploaded
        self.assertFalse(
            education.has_document
        )  # has_document property should be False

    def test_education_has_video_property(self):
        """Test has_video property"""
        from content.models import Education
        from django.core.files.uploadedfile import SimpleUploadedFile

        education = Education.objects.create(**self.valid_education_data)

        # Initially should be False
        self.assertFalse(education.has_video)

        # Create a mock video file
        mock_video = SimpleUploadedFile(
            "test_video.mp4", b"fake video content", content_type="video/mp4"
        )
        education.video = mock_video
        education.save()

        # Refresh from database
        education.refresh_from_db()

        # Now should be True
        self.assertTrue(education.has_video)

    def test_education_has_document_property(self):
        """Test has_document property"""
        from content.models import Education
        from django.core.files.uploadedfile import SimpleUploadedFile

        education = Education.objects.create(**self.valid_education_data)

        # Initially should be False
        self.assertFalse(education.has_document)

        # Create a mock document file
        mock_document = SimpleUploadedFile(
            "test_document.pdf", b"fake pdf content", content_type="application/pdf"
        )
        education.document = mock_document
        education.save()

        # Refresh from database
        education.refresh_from_db()

        # Now should be True
        self.assertTrue(education.has_document)

    def test_education_video_filename_property(self):
        """Test video_filename property"""
        from content.models import Education
        from django.core.files.uploadedfile import SimpleUploadedFile

        education = Education.objects.create(**self.valid_education_data)

        # Should return None when no video
        self.assertIsNone(education.video_filename)

        # Add video
        mock_video = SimpleUploadedFile(
            "my_awesome_video.mp4", b"fake video content", content_type="video/mp4"
        )
        education.video = mock_video
        education.save()
        education.refresh_from_db()

        # Should return a random filename with correct extension
        self.assertIsNotNone(education.video_filename)
        self.assertTrue(education.video_filename.endswith(".mp4"))
        # Verify it's a UUID hex string (32 chars) + extension
        filename_without_ext = education.video_filename.rsplit(".", 1)[0]
        self.assertEqual(len(filename_without_ext), 32)  # UUID hex is 32 characters

    def test_education_document_filename_property(self):
        """Test document_filename property"""
        from content.models import Education
        from django.core.files.uploadedfile import SimpleUploadedFile

        education = Education.objects.create(**self.valid_education_data)

        # Should return None when no document
        self.assertIsNone(education.document_filename)

        # Add document
        mock_document = SimpleUploadedFile(
            "my_presentation.pptx",
            b"fake pptx content",
            content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
        education.document = mock_document
        education.save()
        education.refresh_from_db()

        # Should return a random filename with correct extension
        self.assertIsNotNone(education.document_filename)
        self.assertTrue(education.document_filename.endswith(".pptx"))
        # Verify it's a UUID hex string (32 chars) + extension
        filename_without_ext = education.document_filename.rsplit(".", 1)[0]
        self.assertEqual(len(filename_without_ext), 32)  # UUID hex is 32 characters

    def test_education_with_both_video_and_document(self):
        """Test education with both video and document files"""
        from content.models import Education
        from django.core.files.uploadedfile import SimpleUploadedFile

        education = Education.objects.create(**self.valid_education_data)

        # Add both files
        mock_video = SimpleUploadedFile(
            "tutorial.mp4", b"fake video content", content_type="video/mp4"
        )
        mock_document = SimpleUploadedFile(
            "slides.pdf", b"fake pdf content", content_type="application/pdf"
        )

        education.video = mock_video
        education.document = mock_document
        education.save()
        education.refresh_from_db()

        # Both should exist
        self.assertTrue(education.has_video)
        self.assertTrue(education.has_document)
        self.assertIsNotNone(education.video_filename)
        self.assertIsNotNone(education.document_filename)

    def test_education_random_filenames_are_unique(self):
        """Test that uploaded files get unique random filenames"""
        from content.models import Education
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create two education items with same filename
        education1 = Education.objects.create(
            title="آموزش اول",
            description="توضیحات",
            publish_date=self.valid_education_data["publish_date"],
        )
        education2 = Education.objects.create(
            title="آموزش دوم",
            description="توضیحات",
            publish_date=self.valid_education_data["publish_date"],
        )

        # Upload files with the same original name
        video1 = SimpleUploadedFile(
            "same_name.mp4", b"content1", content_type="video/mp4"
        )
        video2 = SimpleUploadedFile(
            "same_name.mp4", b"content2", content_type="video/mp4"
        )

        education1.video = video1
        education2.video = video2
        education1.save()
        education2.save()

        education1.refresh_from_db()
        education2.refresh_from_db()

        # Filenames should be different (random UUIDs)
        self.assertNotEqual(education1.video_filename, education2.video_filename)

        # Both should have .mp4 extension
        self.assertTrue(education1.video_filename.endswith(".mp4"))
        self.assertTrue(education2.video_filename.endswith(".mp4"))

        # Both should be 32-char UUID + extension
        self.assertEqual(len(education1.video_filename.rsplit(".", 1)[0]), 32)
        self.assertEqual(len(education2.video_filename.rsplit(".", 1)[0]), 32)


class EventModelTest(TestCase):
    """Test cases for Event model"""

    def setUp(self):
        """Set up test data"""
        self.valid_event_data = {
            "title": "مراسم اختتامیه جشنواره",
            "description": "مراسم اختتامیه یازدهمین جشنواره رسانه‌ای ابوذر با حضور مقامات.",
            "publish_date": timezone.now().date(),
        }

    def test_create_event_success(self):
        """Test creating a valid event item"""
        from content.models import Event

        event = Event.objects.create(**self.valid_event_data)

        self.assertEqual(event.title, "مراسم اختتامیه جشنواره")
        self.assertEqual(
            event.description,
            "مراسم اختتامیه یازدهمین جشنواره رسانه‌ای ابوذر با حضور مقامات.",
        )
        self.assertEqual(event.publish_date, self.valid_event_data["publish_date"])

    def test_event_string_representation(self):
        """Test string representation of Event"""
        from content.models import Event

        event = Event.objects.create(**self.valid_event_data)
        self.assertEqual(str(event), "مراسم اختتامیه جشنواره")

    def test_event_tags_functionality(self):
        """Test taggit tags functionality"""
        from content.models import Event

        event = Event.objects.create(**self.valid_event_data)
        event.tags.add("رویداد", "جشنواره", "اختتامیه")

        self.assertEqual(event.tags.count(), 3)
        self.assertIn("رویداد", [tag.name for tag in event.tags.all()])

    def test_event_meta_options(self):
        """Test model meta options"""
        from content.models import Event

        self.assertEqual(Event._meta.verbose_name, "رویداد")
        self.assertEqual(Event._meta.verbose_name_plural, "رویدادها")
        self.assertEqual(Event._meta.ordering, ["-publish_date"])


class ContentModelIntegrationTest(TestCase):
    """Integration tests for all content models"""

    def test_all_models_have_same_structure(self):
        """Test that all three models have the same field structure"""
        from content.models import News, Education, Event

        models = [News, Education, Event]
        expected_fields = [
            "title",
            "description",
            "image",
            "publish_date",
            "tags",
            "created_at",
            "updated_at",
        ]

        for model in models:
            model_fields = [field.name for field in model._meta.fields] + [
                field.name for field in model._meta.many_to_many
            ]

            for expected_field in expected_fields:
                self.assertIn(
                    expected_field,
                    model_fields,
                    f"{model.__name__} missing field: {expected_field}",
                )

    def test_taggit_integration_across_models(self):
        """Test that taggit works consistently across all models"""
        from content.models import News, Education, Event

        # Create instances
        news = News.objects.create(
            title="اخبار تست", description="توضیحات", publish_date=timezone.now().date()
        )
        education = Education.objects.create(
            title="آموزش تست", description="توضیحات", publish_date=timezone.now().date()
        )
        event = Event.objects.create(
            title="رویداد تست",
            description="توضیحات",
            publish_date=timezone.now().date(),
        )

        # Add same tag to all
        common_tag = "تست"
        news.tags.add(common_tag)
        education.tags.add(common_tag)
        event.tags.add(common_tag)

        # Verify tag exists and is shared
        tag = Tag.objects.get(name=common_tag)
        self.assertTrue(tag)

        # Each model should have the tag
        self.assertIn(common_tag, [tag.name for tag in news.tags.all()])
        self.assertIn(common_tag, [tag.name for tag in education.tags.all()])
        self.assertIn(common_tag, [tag.name for tag in event.tags.all()])
