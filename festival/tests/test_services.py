"""
Festival Services Tests
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from festival.services import create_festival_registration
from festival.models import FestivalRegistration
from province.models import Province, City

User = get_user_model()


class FestivalServicesTest(TestCase):
    """Test cases for Festival services"""

    def setUp(self):
        """Set up test data"""
        # Create test province and city
        self.province = Province.objects.create(name="تهران", slug="tehran")
        self.city = City.objects.create(
            name="تهران", slug="tehran-city", province=self.province
        )

        # Valid registration data
        self.valid_registration_data = {
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

    def test_create_festival_registration_new_user(self):
        """Test creating festival registration with new user"""
        phone_number = "09123456789"

        # Ensure user doesn't exist
        self.assertFalse(User.objects.filter(phone=phone_number).exists())

        registration, user_created = create_festival_registration(
            phone_number=phone_number, registration_data=self.valid_registration_data
        )

        # Check that user was created
        self.assertTrue(user_created)
        self.assertTrue(User.objects.filter(phone=phone_number).exists())

        # Check that registration was created
        self.assertIsInstance(registration, FestivalRegistration)
        self.assertEqual(registration.user.phone, phone_number)
        self.assertEqual(registration.full_name, "علی احمدی")
        self.assertEqual(registration.province, self.province)
        self.assertEqual(registration.city, self.city)

    def test_create_festival_registration_existing_user(self):
        """Test creating festival registration with existing user"""
        phone_number = "09123456789"

        # Create existing user
        existing_user = User.objects.create(phone=phone_number, fullName="نام قبلی")

        registration, user_created = create_festival_registration(
            phone_number=phone_number, registration_data=self.valid_registration_data
        )

        # Check that user was not created (already existed)
        self.assertFalse(user_created)
        self.assertEqual(User.objects.filter(phone=phone_number).count(), 1)

        # Check that registration was created with existing user
        self.assertIsInstance(registration, FestivalRegistration)
        self.assertEqual(registration.user, existing_user)
        self.assertEqual(registration.full_name, "علی احمدی")

    def test_create_festival_registration_updates_user_name(self):
        """Test that user's fullName is updated if empty"""
        phone_number = "09123456789"

        # Create existing user without fullName
        existing_user = User.objects.create(phone=phone_number)
        self.assertEqual(existing_user.fullName, "")

        registration, user_created = create_festival_registration(
            phone_number=phone_number, registration_data=self.valid_registration_data
        )

        # Check that user's fullName was updated
        existing_user.refresh_from_db()
        self.assertEqual(existing_user.fullName, "علی احمدی")

    def test_create_festival_registration_preserves_existing_user_name(self):
        """Test that existing user's fullName is preserved if already set"""
        phone_number = "09123456789"
        original_name = "نام اصلی"

        # Create existing user with fullName
        existing_user = User.objects.create(phone=phone_number, fullName=original_name)

        registration, user_created = create_festival_registration(
            phone_number=phone_number, registration_data=self.valid_registration_data
        )

        # Check that user's fullName was preserved
        existing_user.refresh_from_db()
        self.assertEqual(existing_user.fullName, original_name)

    def test_create_festival_registration_transaction_rollback(self):
        """Test that transaction rolls back on error"""
        phone_number = "09123456789"

        # Create invalid data that will cause an IntegrityError (duplicate national_id)
        # First create a registration
        create_festival_registration(
            phone_number="09111111111", registration_data=self.valid_registration_data
        )

        # Count users and registrations after first creation
        initial_user_count = User.objects.count()
        initial_registration_count = FestivalRegistration.objects.count()

        # Try to create another with same national_id (should fail)
        duplicate_data = self.valid_registration_data.copy()
        duplicate_data["phone_number"] = phone_number

        with self.assertRaises(IntegrityError):
            create_festival_registration(
                phone_number=phone_number, registration_data=duplicate_data
            )

        # Check that no additional user was created due to rollback
        self.assertEqual(User.objects.count(), initial_user_count)
        self.assertEqual(
            FestivalRegistration.objects.count(), initial_registration_count
        )

    def test_create_festival_registration_with_duplicate_national_id(self):
        """Test handling duplicate national_id"""
        phone_number1 = "09123456789"
        phone_number2 = "09987654321"

        # Create first registration
        registration1, user_created1 = create_festival_registration(
            phone_number=phone_number1, registration_data=self.valid_registration_data
        )

        # Try to create second registration with same national_id but different phone
        duplicate_data = self.valid_registration_data.copy()
        duplicate_data["phone_number"] = phone_number2

        with self.assertRaises(IntegrityError):
            create_festival_registration(
                phone_number=phone_number2, registration_data=duplicate_data
            )

    def test_create_festival_registration_phone_mismatch(self):
        """Test registration creation when phone_number in data doesn't match service parameter"""
        service_phone = "09123456789"
        data_phone = "09987654321"

        registration_data = self.valid_registration_data.copy()
        registration_data["phone_number"] = data_phone

        registration, user_created = create_festival_registration(
            phone_number=service_phone, registration_data=registration_data
        )

        # The service should create user based on service parameter, not data
        self.assertTrue(User.objects.filter(phone=service_phone).exists())
        self.assertEqual(registration.user.phone, service_phone)
        # But the registration should store the phone from data
        self.assertEqual(registration.phone_number, data_phone)

    def test_create_festival_registration_missing_required_data(self):
        """Test registration creation with missing required data"""
        phone_number = "09123456789"

        # Remove required field - this might not raise TypeError since Django allows None
        # but it should raise an IntegrityError when saved
        incomplete_data = self.valid_registration_data.copy()
        incomplete_data["full_name"] = None  # Set to None instead of deleting

        with self.assertRaises((TypeError, IntegrityError)):
            create_festival_registration(
                phone_number=phone_number, registration_data=incomplete_data
            )

    def test_create_festival_registration_with_none_values(self):
        """Test registration creation with None values for optional fields"""
        phone_number = "09123456789"

        data_with_nones = self.valid_registration_data.copy()
        data_with_nones["virtual_number"] = None
        data_with_nones["special_section"] = None

        registration, user_created = create_festival_registration(
            phone_number=phone_number, registration_data=data_with_nones
        )

        self.assertIsNone(registration.virtual_number)
        self.assertIsNone(registration.special_section)

    def test_create_festival_registration_database_integrity(self):
        """Test database integrity constraints"""
        phone_number = "09123456789"

        # Test with None for required foreign key
        invalid_data = self.valid_registration_data.copy()
        invalid_data["province"] = None  # Required field is None

        with self.assertRaises(IntegrityError):
            create_festival_registration(
                phone_number=phone_number, registration_data=invalid_data
            )

    def test_create_festival_registration_concurrent_access(self):
        """Test handling concurrent access to user creation"""
        phone_number = "09123456789"

        # This test simulates what happens if two requests try to create
        # a user with the same phone number simultaneously

        # First call should succeed
        registration1, user_created1 = create_festival_registration(
            phone_number=phone_number, registration_data=self.valid_registration_data
        )

        # Second call with different registration data should use existing user
        different_data = self.valid_registration_data.copy()
        different_data["full_name"] = "نام متفاوت"
        different_data["national_id"] = "0987654321"

        registration2, user_created2 = create_festival_registration(
            phone_number=phone_number, registration_data=different_data
        )

        # Check that same user was used
        self.assertTrue(user_created1)
        self.assertFalse(user_created2)
        self.assertEqual(registration1.user, registration2.user)
        self.assertEqual(User.objects.filter(phone=phone_number).count(), 1)

    def test_service_returns_correct_types(self):
        """Test that service returns correct types"""
        phone_number = "09123456789"

        result = create_festival_registration(
            phone_number=phone_number, registration_data=self.valid_registration_data
        )

        # Should return tuple with (registration, user_created)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

        registration, user_created = result
        self.assertIsInstance(registration, FestivalRegistration)
        self.assertIsInstance(user_created, bool)
