"""
Tests for Festival Category Models (Format, Topic, Special Section)
"""
from django.test import TestCase
from django.db import IntegrityError
from festival.models import FestivalFormat, FestivalTopic, FestivalSpecialSection


class FestivalFormatModelTest(TestCase):
    """Test cases for FestivalFormat model"""

    def test_create_festival_format_success(self):
        """Test creating a valid festival format"""
        format_obj = FestivalFormat.objects.create(
            code="test_news_report",
            name="گزارش خبری تست",
            description="گزارش‌های خبری و تحلیلی",
        )
        self.assertEqual(format_obj.code, "test_news_report")
        self.assertEqual(format_obj.name, "گزارش خبری تست")
        self.assertTrue(format_obj.is_active)

    def test_festival_format_unique_code(self):
        """Test that format code must be unique"""
        FestivalFormat.objects.create(code="test_interview_1", name="مصاحبه")
        with self.assertRaises(IntegrityError):
            FestivalFormat.objects.create(code="test_interview_1", name="مصاحبه دیگر")

    def test_festival_format_str_representation(self):
        """Test string representation of festival format"""
        format_obj = FestivalFormat.objects.create(code="test_photo_1", name="عکس")
        self.assertEqual(str(format_obj), "عکس")

    def test_festival_format_ordering(self):
        """Test that formats are ordered by name"""
        FestivalFormat.objects.create(code="test_doc_1", name="مستند")
        FestivalFormat.objects.create(code="test_news_1", name="اخبار")
        FestivalFormat.objects.create(code="test_vid_1", name="ویدیو")

        formats = list(
            FestivalFormat.objects.filter(code__startswith="test_").order_by("name")
        )
        self.assertEqual(formats[0].name, "اخبار")
        self.assertEqual(formats[1].name, "مستند")
        self.assertEqual(formats[2].name, "ویدیو")

    def test_festival_format_is_active_default(self):
        """Test that is_active defaults to True"""
        format_obj = FestivalFormat.objects.create(code="test", name="تست")
        self.assertTrue(format_obj.is_active)

    def test_festival_format_optional_fields(self):
        """Test that description and display_order are optional"""
        format_obj = FestivalFormat.objects.create(code="test_optional_1", name="تست")
        self.assertIsNone(format_obj.description)
        self.assertEqual(format_obj.display_order, 0)


class FestivalTopicModelTest(TestCase):
    """Test cases for FestivalTopic model"""

    def test_create_festival_topic_success(self):
        """Test creating a valid festival topic"""
        topic = FestivalTopic.objects.create(
            code="test_year_slogan", name="شعار سال تست", description="محور شعار سال"
        )
        self.assertEqual(topic.code, "test_year_slogan")
        self.assertEqual(topic.name, "شعار سال تست")
        self.assertTrue(topic.is_active)

    def test_festival_topic_unique_code(self):
        """Test that topic code must be unique"""
        FestivalTopic.objects.create(code="test_jihad_1", name="جهاد تبیین")
        with self.assertRaises(IntegrityError):
            FestivalTopic.objects.create(code="test_jihad_1", name="جهاد تبیین دیگر")

    def test_festival_topic_str_representation(self):
        """Test string representation of festival topic"""
        topic = FestivalTopic.objects.create(code="test_hope_1", name="امید و نشاط")
        self.assertEqual(str(topic), "امید و نشاط")

    def test_festival_topic_ordering(self):
        """Test that topics are ordered by name"""
        FestivalTopic.objects.create(code="test_top_a", name="ز")
        FestivalTopic.objects.create(code="test_top_b", name="الف")
        FestivalTopic.objects.create(code="test_top_c", name="ب")

        topics = list(
            FestivalTopic.objects.filter(code__startswith="test_top_").order_by("name")
        )
        self.assertEqual(topics[0].name, "الف")
        self.assertEqual(topics[1].name, "ب")
        self.assertEqual(topics[2].name, "ز")

    def test_festival_topic_is_active_default(self):
        """Test that is_active defaults to True"""
        topic = FestivalTopic.objects.create(code="test", name="تست")
        self.assertTrue(topic.is_active)


class FestivalSpecialSectionModelTest(TestCase):
    """Test cases for FestivalSpecialSection model"""

    def test_create_special_section_success(self):
        """Test creating a valid special section"""
        section = FestivalSpecialSection.objects.create(
            code="test_progress_1",
            name="روایت پیشرفت تست",
            description="بخش ویژه روایت پیشرفت",
        )
        self.assertEqual(section.code, "test_progress_1")
        self.assertEqual(section.name, "روایت پیشرفت تست")
        self.assertTrue(section.is_active)

    def test_special_section_unique_code(self):
        """Test that section code must be unique"""
        FestivalSpecialSection.objects.create(code="test_field_1", name="روایت میدان")
        with self.assertRaises(IntegrityError):
            FestivalSpecialSection.objects.create(
                code="test_field_1", name="روایت میدان دیگر"
            )

    def test_special_section_str_representation(self):
        """Test string representation of special section"""
        section = FestivalSpecialSection.objects.create(
            code="test_section_1", name="بخش تست"
        )
        self.assertEqual(str(section), "بخش تست")

    def test_special_section_ordering(self):
        """Test that sections are ordered by name"""
        FestivalSpecialSection.objects.create(code="test_sec_a", name="ج")
        FestivalSpecialSection.objects.create(code="test_sec_b", name="الف")
        FestivalSpecialSection.objects.create(code="test_sec_c", name="ب")

        sections = list(
            FestivalSpecialSection.objects.filter(
                code__startswith="test_sec_"
            ).order_by("name")
        )
        self.assertEqual(sections[0].name, "الف")
        self.assertEqual(sections[1].name, "ب")
        self.assertEqual(sections[2].name, "ج")

    def test_special_section_is_active_default(self):
        """Test that is_active defaults to True"""
        section = FestivalSpecialSection.objects.create(code="test", name="تست")
        self.assertTrue(section.is_active)


class FestivalRegistrationWithCategoriesTest(TestCase):
    """Test FestivalRegistration with category models"""

    def setUp(self):
        """Set up test data"""
        from django.contrib.auth import get_user_model
        from province.models import Province, City
        from festival.models import FestivalRegistration

        User = get_user_model()

        # Create user
        self.user = User.objects.create(phone="09123456789", fullName="علی احمدی")

        # Create province and city
        self.province = Province.objects.create(name="تهران", slug="tehran")
        self.city = City.objects.create(
            name="تهران", slug="tehran-city", province=self.province
        )

        # Create category objects with unique codes
        self.format = FestivalFormat.objects.create(
            code="test_reg_news", name="گزارش خبری"
        )
        self.topic = FestivalTopic.objects.create(
            code="test_reg_slogan", name="شعار سال"
        )
        self.section = FestivalSpecialSection.objects.create(
            code="test_reg_progress", name="روایت پیشرفت"
        )

    def test_create_registration_with_categories(self):
        """Test creating registration with foreign key relationships to categories"""
        from festival.models import FestivalRegistration

        registration = FestivalRegistration.objects.create(
            user=self.user,
            full_name="علی احمدی",
            father_name="حسین",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست",
            festival_format=self.format,
            festival_topic=self.topic,
            special_section=self.section,
        )

        self.assertEqual(registration.festival_format, self.format)
        self.assertEqual(registration.festival_topic, self.topic)
        self.assertEqual(registration.special_section, self.section)
        self.assertEqual(registration.festival_format.name, "گزارش خبری")
        self.assertEqual(registration.festival_topic.name, "شعار سال")

    def test_registration_special_section_optional(self):
        """Test that special_section is optional in registration"""
        from festival.models import FestivalRegistration

        registration = FestivalRegistration.objects.create(
            user=self.user,
            full_name="علی احمدی",
            father_name="حسین",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست",
            festival_format=self.format,
            festival_topic=self.topic,
            special_section=None,
        )

        self.assertIsNone(registration.special_section)

    def test_cascade_delete_format(self):
        """Test that deleting format affects registrations properly"""
        from festival.models import FestivalRegistration

        registration = FestivalRegistration.objects.create(
            user=self.user,
            full_name="علی احمدی",
            father_name="حسین",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست",
            festival_format=self.format,
            festival_topic=self.topic,
        )

        format_id = self.format.id
        self.format.delete()

        # Registration should be deleted due to CASCADE
        with self.assertRaises(FestivalRegistration.DoesNotExist):
            FestivalRegistration.objects.get(id=registration.id)

    def test_active_categories_only(self):
        """Test filtering active categories"""
        FestivalFormat.objects.create(
            code="test_inactive_1", name="غیرفعال", is_active=False
        )

        # Filter by our test codes to avoid counting the migrated data
        active_formats = FestivalFormat.objects.filter(
            code__startswith="test_", is_active=True
        )
        all_test_formats = FestivalFormat.objects.filter(code__startswith="test_")

        self.assertEqual(active_formats.count(), 1)  # Only test_reg_news
        self.assertEqual(all_test_formats.count(), 2)  # test_reg_news + test_inactive_1
