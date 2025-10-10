"""
Festival Registration Model Tests
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from festival.models import FestivalRegistration
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
            "festival_format": "news_report",
            "festival_topic": "year_slogan",
            "special_section": "progress_narrative",
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

    def test_unique_national_id_constraint(self):
        """Test that national_id must be unique"""
        FestivalRegistration.objects.create(**self.valid_data)

        # Try to create another registration with same national_id
        duplicate_data = self.valid_data.copy()
        duplicate_data["user"] = User.objects.create(phone="09987654321")
        duplicate_data["phone_number"] = "09987654321"

        with self.assertRaises(IntegrityError):
            FestivalRegistration.objects.create(**duplicate_data)

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
        """Test validation of choice fields"""
        # Test invalid gender
        data = self.valid_data.copy()
        data["gender"] = "invalid_gender"
        registration = FestivalRegistration(**data)

        with self.assertRaises(ValidationError):
            registration.full_clean()

        # Test invalid festival_format
        data = self.valid_data.copy()
        data["festival_format"] = "invalid_format"
        registration = FestivalRegistration(**data)

        with self.assertRaises(ValidationError):
            registration.full_clean()

        # Test invalid festival_topic
        data = self.valid_data.copy()
        data["festival_topic"] = "invalid_topic"
        registration = FestivalRegistration(**data)

        with self.assertRaises(ValidationError):
            registration.full_clean()

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

        # Test all format choices
        for choice_value, choice_label in FestivalRegistration.FORMAT_CHOICES:
            data = self.valid_data.copy()
            data["festival_format"] = choice_value
            registration = FestivalRegistration(**data)
            registration.full_clean()  # Should not raise ValidationError

        # Test all topic choices
        for choice_value, choice_label in FestivalRegistration.TOPIC_CHOICES:
            data = self.valid_data.copy()
            data["festival_topic"] = choice_value
            registration = FestivalRegistration(**data)
            registration.full_clean()  # Should not raise ValidationError

        # Test all special section choices
        for choice_value, choice_label in FestivalRegistration.SPECIAL_SECTION_CHOICES:
            data = self.valid_data.copy()
            data["special_section"] = choice_value
            registration = FestivalRegistration(**data)
            registration.full_clean()  # Should not raise ValidationError
