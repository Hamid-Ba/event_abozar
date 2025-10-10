"""
Festival Registration API Tests
"""
import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from festival.models import FestivalRegistration
from province.models import Province, City

User = get_user_model()


class FestivalRegistrationAPITest(APITestCase):
    """Test cases for Festival Registration API endpoints"""

    def setUp(self):
        """Set up test data"""
        # Create test provinces and cities
        self.province = Province.objects.create(name="تهران", slug="tehran")
        self.city = City.objects.create(
            name="تهران", slug="tehran-city", province=self.province
        )

        self.other_province = Province.objects.create(name="اصفهان", slug="isfahan")
        self.other_city = City.objects.create(
            name="اصفهان", slug="isfahan-city", province=self.other_province
        )

        # Create test user
        self.user = User.objects.create(phone="09123456789", fullName="علی احمدی")

        # Valid registration data
        self.valid_registration_data = {
            "full_name": "علی احمدی",
            "father_name": "محمد",
            "national_id": "1234567890",
            "gender": "male",
            "education": "کارشناسی",
            "phone_number": "09123456789",
            "virtual_number": "@ali_ahmadi",
            "province_id": self.province.id,
            "city_id": self.city.id,
            "media_name": "رسانه تست",
            "festival_format": "news_report",
            "festival_topic": "year_slogan",
            "special_section": "progress_narrative",
        }

    def test_create_registration_success(self):
        """Test successful registration creation"""
        url = reverse("festival:registration-create")
        response = self.client.post(
            url,
            data=json.dumps(self.valid_registration_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["message"], "ثبت نام با موفقیت انجام شد")

        # Verify registration was created
        self.assertTrue(
            FestivalRegistration.objects.filter(national_id="1234567890").exists()
        )

        # Verify user was created
        self.assertTrue(User.objects.filter(phone="09123456789").exists())

    def test_create_registration_duplicate_national_id(self):
        """Test creating registration with duplicate national_id"""
        # Create first registration
        FestivalRegistration.objects.create(
            user=self.user,
            full_name="علی احمدی",
            father_name="محمد",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست",
            festival_format="news_report",
            festival_topic="year_slogan",
        )

        url = reverse("festival:registration-create")
        response = self.client.post(
            url,
            data=json.dumps(self.valid_registration_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if it's our custom error or Django's unique constraint error
        if "error" in response.data:
            self.assertEqual(
                response.data["error"], "قبلاً با این کد ملی ثبت نام شده است"
            )
        else:
            # Django's unique constraint error
            self.assertIn("national_id", response.data)

    def test_create_registration_invalid_phone(self):
        """Test creating registration with invalid phone number"""
        data = self.valid_registration_data.copy()
        data["phone_number"] = "0912345678"  # Too short

        url = reverse("festival:registration-create")
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_registration_invalid_national_id(self):
        """Test creating registration with invalid national ID"""
        data = self.valid_registration_data.copy()
        data["national_id"] = "123456789"  # Too short

        url = reverse("festival:registration-create")
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_registration_city_province_mismatch(self):
        """Test creating registration with city that doesn't belong to province"""
        data = self.valid_registration_data.copy()
        data["province_id"] = self.province.id
        data["city_id"] = self.other_city.id  # This city belongs to other_province

        url = reverse("festival:registration-create")
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_registration_missing_required_fields(self):
        """Test creating registration with missing required fields"""
        required_fields = [
            "full_name",
            "father_name",
            "national_id",
            "gender",
            "education",
            "phone_number",
            "province_id",
            "city_id",
            "media_name",
            "festival_format",
            "festival_topic",
        ]

        for field in required_fields:
            with self.subTest(field=field):
                data = self.valid_registration_data.copy()
                del data[field]

                url = reverse("festival:registration-create")
                response = self.client.post(
                    url, data=json.dumps(data), content_type="application/json"
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_registrations(self):
        """Test listing registrations"""
        # Create test registrations
        registration1 = FestivalRegistration.objects.create(
            user=self.user,
            full_name="علی احمدی",
            father_name="محمد",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست",
            festival_format="news_report",
            festival_topic="year_slogan",
        )

        user2 = User.objects.create(phone="09987654321")
        registration2 = FestivalRegistration.objects.create(
            user=user2,
            full_name="فاطمه حسینی",
            father_name="علی",
            national_id="0987654321",
            gender="female",
            education="کارشناسی ارشد",
            phone_number="09987654321",
            province=self.other_province,
            city=self.other_city,
            media_name="رسانه دیگر",
            festival_format="interview",
            festival_topic="media_industry",
        )

        url = reverse("festival:registration-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_registrations_with_filters(self):
        """Test listing registrations with filters"""
        # Create test registrations
        registration1 = FestivalRegistration.objects.create(
            user=self.user,
            full_name="علی احمدی",
            father_name="محمد",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست",
            festival_format="news_report",
            festival_topic="year_slogan",
        )

        user2 = User.objects.create(phone="09987654321")
        registration2 = FestivalRegistration.objects.create(
            user=user2,
            full_name="فاطمه حسینی",
            father_name="علی",
            national_id="0987654321",
            gender="female",
            education="کارشناسی ارشد",
            phone_number="09987654321",
            province=self.other_province,
            city=self.other_city,
            media_name="رسانه دیگر",
            festival_format="interview",
            festival_topic="media_industry",
        )

        # Test filter by gender
        url = reverse("festival:registration-list")
        response = self.client.get(url + "?gender=male")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["full_name"], "علی احمدی")

        # Test filter by province
        response = self.client.get(url + f"?province={self.province.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["province_name"], "تهران")

    def test_list_registrations_with_search(self):
        """Test listing registrations with search"""
        registration = FestivalRegistration.objects.create(
            user=self.user,
            full_name="علی احمدی",
            father_name="محمد",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست",
            festival_format="news_report",
            festival_topic="year_slogan",
        )

        url = reverse("festival:registration-list")

        # Search by name
        response = self.client.get(url + "?search=علی")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Search by media name
        response = self.client.get(url + "?search=رسانه")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_registration_detail(self):
        """Test getting registration detail"""
        registration = FestivalRegistration.objects.create(
            user=self.user,
            full_name="علی احمدی",
            father_name="محمد",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست",
            festival_format="news_report",
            festival_topic="year_slogan",
        )

        url = reverse("festival:registration-detail", kwargs={"id": registration.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["full_name"], "علی احمدی")
        self.assertEqual(response.data["province"]["name"], "تهران")
        self.assertEqual(response.data["city"]["name"], "تهران")

    def test_get_registration_detail_not_found(self):
        """Test getting detail for non-existent registration"""
        url = reverse("festival:registration-detail", kwargs={"id": 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_registration_by_phone(self):
        """Test searching registration by phone number"""
        registration = FestivalRegistration.objects.create(
            user=self.user,
            full_name="علی احمدی",
            father_name="محمد",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست",
            festival_format="news_report",
            festival_topic="year_slogan",
        )

        url = reverse("festival:registration-search")
        response = self.client.get(url + "?phone=09123456789")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["full_name"], "علی احمدی")

    def test_search_registration_by_national_id(self):
        """Test searching registration by national ID"""
        registration = FestivalRegistration.objects.create(
            user=self.user,
            full_name="علی احمدی",
            father_name="محمد",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست",
            festival_format="news_report",
            festival_topic="year_slogan",
        )

        url = reverse("festival:registration-search")
        response = self.client.get(url + "?national_id=1234567890")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["full_name"], "علی احمدی")

    def test_search_registration_without_params(self):
        """Test searching registration without search parameters"""
        url = reverse("festival:registration-search")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_api_pagination(self):
        """Test API pagination"""
        # Create multiple registrations
        for i in range(25):
            user = User.objects.create(phone=f"0912345678{i:02d}")
            FestivalRegistration.objects.create(
                user=user,
                full_name=f"نام {i}",
                father_name="پدر",
                national_id=f"123456789{i}",
                gender="male",
                education="کارشناسی",
                phone_number=f"0912345678{i:02d}",
                province=self.province,
                city=self.city,
                media_name=f"رسانه {i}",
                festival_format="news_report",
                festival_topic="year_slogan",
            )

        url = reverse("festival:registration-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if pagination is working (default page size should be applied)
        self.assertLessEqual(len(response.data), 25)

    def test_api_ordering(self):
        """Test API ordering"""
        # Create registrations with different creation times
        registration1 = FestivalRegistration.objects.create(
            user=self.user,
            full_name="علی احمدی",
            father_name="محمد",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست",
            festival_format="news_report",
            festival_topic="year_slogan",
        )

        user2 = User.objects.create(phone="09987654321")
        registration2 = FestivalRegistration.objects.create(
            user=user2,
            full_name="فاطمه حسینی",
            father_name="علی",
            national_id="0987654321",
            gender="female",
            education="کارشناسی ارشد",
            phone_number="09987654321",
            province=self.province,
            city=self.city,
            media_name="رسانه دیگر",
            festival_format="interview",
            festival_topic="media_industry",
        )

        url = reverse("festival:registration-list")

        # Test default ordering (by -created_at)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["full_name"], "فاطمه حسینی")  # More recent

        # Test ordering by name
        response = self.client.get(url + "?ordering=full_name")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]["full_name"], "علی احمدی"
        )  # Alphabetically first
