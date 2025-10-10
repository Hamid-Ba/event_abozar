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
