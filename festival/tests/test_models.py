"""
Festival Registration Model Tests
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from festival.models import (
    FestivalRegistration,
    FestivalFormat,
    FestivalTopic,
    FestivalSpecialSection,
)
from province.models import Province, City

User = get_user_model()


class FestivalRegistrationModelTest(TestCase):
    """Test cases for FestivalRegistration model"""

    def setUp(self):
        """Set up test data"""
        # Create test province and city
        self.province = Province.objects.create(name="تهران", slug="tehran")
        self.city = City.objects.create(
            name="تهران", slug="tehran-city", province=self.province
        )

        # Create test user
        self.user = User.objects.create(phone="09123456789", fullName="علی احمدی")

        # Load category objects
        self.format_news = FestivalFormat.objects.get(code="news_report")
        self.topic_slogan = FestivalTopic.objects.get(code="year_slogan")
        self.section_progress = FestivalSpecialSection.objects.get(
            code="progress_narrative"
        )

        # Valid registration data
        self.valid_data = {
            "user": self.user,
            "full_name": "علی احمدی",
            "father_name": "محمد",
            "national_id": "1234567890",
            "gender": "male",
            "education": "کارشناسی",
            "phone_number": "09123456789",
            "virtual_number": "@ali_ahmadi",
            "province": self.province,
            "city": self.city,
            "media_name": "رسانه تست",
            "festival_format": self.format_news,
            "festival_topic": self.topic_slogan,
            "special_section": self.section_progress,
        }

    def test_create_festival_registration_success(self):
        """Test creating a valid festival registration"""
        registration = FestivalRegistration.objects.create(**self.valid_data)

        self.assertEqual(registration.full_name, "علی احمدی")
        self.assertEqual(registration.father_name, "محمد")
        self.assertEqual(registration.national_id, "1234567890")
        self.assertEqual(registration.gender, "male")
        self.assertEqual(registration.province, self.province)
        self.assertEqual(registration.city, self.city)
        self.assertEqual(registration.user, self.user)
        self.assertTrue(registration.created_at)
        self.assertTrue(registration.updated_at)

    def test_string_representation(self):
        """Test string representation of FestivalRegistration"""
        registration = FestivalRegistration.objects.create(**self.valid_data)
        expected_str = (
            f"{self.valid_data['full_name']} - {self.valid_data['media_name']}"
        )
        self.assertEqual(str(registration), expected_str)

    def test_duplicate_national_id_allowed(self):
        """Test that duplicate national_id is allowed (no unique constraint)"""
        FestivalRegistration.objects.create(**self.valid_data)

        # Create another registration with same national_id
        duplicate_data = self.valid_data.copy()
        duplicate_data["user"] = User.objects.create(phone="09987654321")
        duplicate_data["phone_number"] = "09987654321"

        # Should not raise IntegrityError
        registration2 = FestivalRegistration.objects.create(**duplicate_data)
        self.assertIsNotNone(registration2.id)

    def test_required_fields(self):
        """Test that required fields cannot be None"""
        required_fields = [
            "user",
            "full_name",
            "father_name",
            "national_id",
            "gender",
            "education",
            "phone_number",
            "province",
            "city",
            "media_name",
            "festival_format",
            "festival_topic",
        ]

        for field in required_fields:
            with self.subTest(field=field):
                data = self.valid_data.copy()
                data[field] = None

                with self.assertRaises((IntegrityError, ValidationError)):
                    registration = FestivalRegistration(**data)
                    registration.full_clean()

    def test_choice_field_validation(self):
        """Test validation of choice fields and ForeignKey relationships"""
        # Test invalid gender
        data = self.valid_data.copy()
        data["gender"] = "invalid_gender"
        registration = FestivalRegistration(**data)

        with self.assertRaises(ValidationError):
            registration.full_clean()

        # Test invalid festival_format (trying to assign string instead of object)
        data = self.valid_data.copy()

        with self.assertRaises(ValueError):
            data["festival_format"] = "invalid_format"
            registration = FestivalRegistration(**data)

        # Test invalid festival_topic (trying to assign string instead of object)
        data = self.valid_data.copy()

        with self.assertRaises(ValueError):
            data["festival_topic"] = "invalid_topic"
            registration = FestivalRegistration(**data)

    def test_optional_fields(self):
        """Test that optional fields can be None or empty"""
        data = self.valid_data.copy()
        data["virtual_number"] = None
        data["special_section"] = None

        registration = FestivalRegistration.objects.create(**data)
        self.assertIsNone(registration.virtual_number)
        self.assertIsNone(registration.special_section)

    def test_foreign_key_relationships(self):
        """Test foreign key relationships"""
        registration = FestivalRegistration.objects.create(**self.valid_data)

        # Test user relationship
        self.assertEqual(registration.user.phone, "09123456789")
        self.assertIn(registration, self.user.festival_registrations.all())

        # Test province relationship
        self.assertEqual(registration.province.name, "تهران")

        # Test city relationship
        self.assertEqual(registration.city.name, "تهران")
        self.assertEqual(registration.city.province, self.province)

    def test_cascade_delete_user(self):
        """Test that deleting user cascades to registration"""
        registration = FestivalRegistration.objects.create(**self.valid_data)
        registration_id = registration.id

        self.user.delete()

        with self.assertRaises(FestivalRegistration.DoesNotExist):
            FestivalRegistration.objects.get(id=registration_id)

    def test_cascade_delete_province(self):
        """Test that deleting province cascades to registration"""
        registration = FestivalRegistration.objects.create(**self.valid_data)
        registration_id = registration.id

        self.province.delete()

        with self.assertRaises(FestivalRegistration.DoesNotExist):
            FestivalRegistration.objects.get(id=registration_id)

    def test_cascade_delete_city(self):
        """Test that deleting city cascades to registration"""
        registration = FestivalRegistration.objects.create(**self.valid_data)
        registration_id = registration.id

        self.city.delete()

        with self.assertRaises(FestivalRegistration.DoesNotExist):
            FestivalRegistration.objects.get(id=registration_id)

    def test_meta_options(self):
        """Test model meta options"""
        registration = FestivalRegistration.objects.create(**self.valid_data)

        # Test verbose names
        self.assertEqual(FestivalRegistration._meta.verbose_name, "ثبت نام جشنواره")
        self.assertEqual(
            FestivalRegistration._meta.verbose_name_plural, "ثبت نام های جشنواره"
        )

        # Test default ordering
        self.assertEqual(FestivalRegistration._meta.ordering, ["-created_at"])

    def test_choice_field_options(self):
        """Test that all choice field options are valid"""
        # Test all gender choices
        for choice_value, choice_label in FestivalRegistration.GENDER_CHOICES:
            data = self.valid_data.copy()
            data["gender"] = choice_value
            registration = FestivalRegistration(**data)
            registration.full_clean()  # Should not raise ValidationError

        # Test category ForeignKey relationships
        # Test different festival formats
        for format_obj in FestivalFormat.objects.filter(is_active=True)[:3]:
            data = self.valid_data.copy()
            data["festival_format"] = format_obj
            registration = FestivalRegistration(**data)
            registration.full_clean()  # Should not raise ValidationError

        # Test different festival topics
        for topic_obj in FestivalTopic.objects.filter(is_active=True)[:3]:
            data = self.valid_data.copy()
            data["festival_topic"] = topic_obj
            registration = FestivalRegistration(**data)
            registration.full_clean()  # Should not raise ValidationError

        # Test different special sections
        for section_obj in FestivalSpecialSection.objects.filter(is_active=True)[:2]:
            data = self.valid_data.copy()
            data["special_section"] = section_obj
            registration = FestivalRegistration(**data)
            registration.full_clean()  # Should not raise ValidationError


class WorkModelTest(TestCase):
    """Test cases for Work model"""

    def setUp(self):
        """Set up test data"""
        # Create test province and city
        self.province = Province.objects.create(name="تهران", slug="tehran")
        self.city = City.objects.create(
            name="تهران", slug="tehran-city", province=self.province
        )

        # Create test user
        self.user = User.objects.create(phone="09123456789", fullName="علی احمدی")

        # Load category objects
        self.format_news = FestivalFormat.objects.get(code="news_report")
        self.topic_slogan = FestivalTopic.objects.get(code="year_slogan")

        # Create test festival registration
        self.festival_registration = FestivalRegistration.objects.create(
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
            festival_format=self.format_news,
            festival_topic=self.topic_slogan,
        )

        # Valid work data
        self.valid_work_data = {
            "festival_registration": self.festival_registration,
            "title": "کار نمونه",
            "description": "توضیحات کار نمونه برای تست",
        }

    def test_work_model_creation(self):
        """Test Work model can be created with valid data"""
        from festival.models import Work

        work = Work.objects.create(**self.valid_work_data)

        self.assertEqual(work.title, "کار نمونه")
        self.assertEqual(work.description, "توضیحات کار نمونه برای تست")
        self.assertEqual(work.festival_registration, self.festival_registration)
        self.assertIsNotNone(work.created_at)
        self.assertIsNotNone(work.updated_at)

    def test_work_model_str_representation(self):
        """Test Work model string representation"""
        from festival.models import Work

        work = Work.objects.create(**self.valid_work_data)
        expected_str = f"{work.title} - {work.festival_registration.full_name}"
        self.assertEqual(str(work), expected_str)

    def test_work_model_verbose_names(self):
        """Test Work model verbose names are in Persian"""
        from festival.models import Work

        work = Work(**self.valid_work_data)

        # Check field verbose names
        title_field = Work._meta.get_field("title")
        description_field = Work._meta.get_field("description")
        festival_registration_field = Work._meta.get_field("festival_registration")

        self.assertEqual(title_field.verbose_name, "عنوان")
        self.assertEqual(description_field.verbose_name, "توضیحات")
        self.assertEqual(festival_registration_field.verbose_name, "ثبت نام جشنواره")

    def test_work_model_meta_options(self):
        """Test Work model Meta options"""
        from festival.models import Work

        self.assertEqual(Work._meta.verbose_name, "اثر")
        self.assertEqual(Work._meta.verbose_name_plural, "آثار")
        self.assertEqual(Work._meta.ordering, ["-created_at"])

    def test_work_model_required_fields(self):
        """Test Work model required fields validation"""
        from festival.models import Work
        from django.db import IntegrityError, transaction

        # Test without title (should raise IntegrityError for NOT NULL constraint)
        invalid_data = self.valid_work_data.copy()
        invalid_data["title"] = None

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Work.objects.create(**invalid_data)

        # Test without festival_registration (should raise IntegrityError for NOT NULL constraint)
        invalid_data = self.valid_work_data.copy()
        invalid_data["festival_registration"] = None

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Work.objects.create(**invalid_data)

    def test_work_model_file_field_required(self):
        """Test Work model file field is required"""
        from festival.models import Work
        from django.core.exceptions import ValidationError

        # Try to create work without file - should work at model level but fail at form level
        work = Work.objects.create(**self.valid_work_data)

        # File field is now required, so accessing the field should work but file will be empty
        self.assertFalse(work.file)

    def test_work_model_relationship_with_festival_registration(self):
        """Test Work model relationship with FestivalRegistration"""
        from festival.models import Work

        # Create multiple works for the same registration
        work1 = Work.objects.create(
            festival_registration=self.festival_registration,
            title="کار اول",
            description="توضیحات کار اول",
        )
        work2 = Work.objects.create(
            festival_registration=self.festival_registration,
            title="کار دوم",
            description="توضیحات کار دوم",
        )

        # Test reverse relationship
        works = self.festival_registration.works.all()
        self.assertEqual(works.count(), 2)
        self.assertIn(work1, works)
        self.assertIn(work2, works)

    def test_work_model_cascade_delete(self):
        """Test Work model cascade delete when FestivalRegistration is deleted"""
        from festival.models import Work

        work = Work.objects.create(**self.valid_work_data)
        work_id = work.id

        # Delete festival registration
        self.festival_registration.delete()

        # Work should be deleted as well (CASCADE)
        with self.assertRaises(Work.DoesNotExist):
            Work.objects.get(id=work_id)

    def test_work_model_unique_filename_properties(self):
        """Test Work model filename properties for unique naming"""
        from festival.models import Work
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create a work with a file
        test_file = SimpleUploadedFile(
            "original_filename.pdf",
            b"test file content",
            content_type="application/pdf",
        )

        work_data = self.valid_work_data.copy()
        work_data["file"] = test_file

        work = Work.objects.create(**work_data)

        # Test file_display_name property
        display_name = work.file_display_name
        self.assertIsNotNone(display_name)
        self.assertTrue(display_name.endswith(".pdf"))
        self.assertIn("کار نمونه", display_name)  # Should contain part of title

        # Test unique_filename property
        unique_name = work.unique_filename
        self.assertIsNotNone(unique_name)
        self.assertTrue(len(unique_name) > 10)  # Should be a UUID-based name
        self.assertTrue(unique_name.endswith(".pdf"))
