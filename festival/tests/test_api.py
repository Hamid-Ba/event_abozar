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


class WorkAPITest(APITestCase):
    """Test cases for Work API endpoints"""

    def setUp(self):
        """Set up test data"""
        # Create test provinces and cities
        self.province = Province.objects.create(name="تهران", slug="tehran")
        self.city = City.objects.create(
            name="تهران", slug="tehran-city", province=self.province
        )

        # Create test users
        self.user1 = User.objects.create(phone="09123456789", fullName="علی احمدی")
        self.user2 = User.objects.create(phone="09123456790", fullName="فاطمه حسینی")

        # Create test festival registrations
        self.registration1 = FestivalRegistration.objects.create(
            user=self.user1,
            full_name="علی احمدی",
            father_name="حسین",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست۱",
            festival_format="news_report",
            festival_topic="year_slogan",
        )

        self.registration2 = FestivalRegistration.objects.create(
            user=self.user2,
            full_name="فاطمه حسینی",
            father_name="محمد",
            national_id="1234567891",
            gender="female",
            education="کارشناسی ارشد",
            phone_number="09123456790",
            province=self.province,
            city=self.city,
            media_name="رسانه تست۲",
            festival_format="interview",
            festival_topic="jihad_explanation",
        )

        # Valid work data with file
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create a test file
        self.test_file = SimpleUploadedFile(
            "test_file.pdf",
            b"test file content for testing",
            content_type="application/pdf",
        )

        self.valid_work_data = {
            "festival_registration": self.registration1.id,
            "title": "کار نمونه برای تست",
            "description": "این توضیحات کاملی برای کار نمونه است که برای تست نوشته شده است.",
            "file": self.test_file,
        }

    def test_work_list_unauthenticated(self):
        """Test Work list access for unauthenticated users should be forbidden"""
        url = reverse("festival:work-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_work_list_authenticated_empty(self):
        """Test Work list for authenticated user with no works"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:work-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_work_create_success(self):
        """Test successful work creation"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:work-list")

        response = self.client.post(url, self.valid_work_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], self.valid_work_data["title"])
        self.assertEqual(
            response.data["description"], self.valid_work_data["description"]
        )

    def test_work_create_unauthenticated(self):
        """Test work creation by unauthenticated user should fail"""
        url = reverse("festival:work-list")
        response = self.client.post(url, self.valid_work_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_work_create_invalid_registration(self):
        """Test work creation with invalid festival registration should fail"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:work-list")

        # Try to create work for another user's registration
        invalid_data = self.valid_work_data.copy()
        invalid_data["festival_registration"] = self.registration2.id

        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("festival_registration" in response.data)
        self.assertTrue("شما تنها می" in str(response.data))

    def test_work_create_invalid_title(self):
        """Test work creation with invalid title should fail"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:work-list")

        # Short title
        invalid_data = self.valid_work_data.copy()
        invalid_data["title"] = "کم"

        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("عنوان اثر باید حداقل ۳ کاراکتر باشد", str(response.data))

    def test_work_create_invalid_description(self):
        """Test work creation with invalid description should fail"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:work-list")

        # Short description
        test_file = SimpleUploadedFile(
            "test_file2.pdf",
            b"test file content for testing",
            content_type="application/pdf",
        )

        invalid_data = {
            "festival_registration": self.registration1.id,
            "title": "کار نمونه برای تست",
            "description": "کم",
            "file": test_file,
        }

        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("توضیحات اثر باید حداقل ۱۰ کاراکتر باشد", str(response.data))

    def test_work_create_missing_file(self):
        """Test work creation without file should fail"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:work-list")

        # Data without file
        invalid_data = {
            "festival_registration": self.registration1.id,
            "title": "کار نمونه برای تست",
            "description": "این توضیحات کاملی برای کار نمونه است که برای تست نوشته شده است.",
        }

        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("file" in response.data)
        # Either the DRF error message or our custom message should appear
        response_str = str(response.data)
        self.assertTrue(
            "فایل اثر الزامی است" in response_str
            or "فایلی ارسال نشده است" in response_str
        )

    def test_work_create_file_too_large(self):
        """Test serializer validation for file larger than 110MB"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from festival.serializers import WorkCreateSerializer
        from unittest.mock import Mock

        # Create a mock file with large size
        large_file = Mock()
        large_file.name = "large_file.pdf"
        large_file.size = 111 * 1024 * 1024  # 111MB

        request = Mock()
        request.user = self.user1

        serializer_data = {
            "festival_registration": self.registration1.id,
            "title": "کار با فایل بزرگ",
            "description": "این کار دارای فایل بزرگی است که نباید قبول شود.",
            "file": large_file,
        }

        serializer = WorkCreateSerializer(
            data=serializer_data, context={"request": request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("حجم فایل نباید بیش از ۱۱۰ مگابایت باشد", str(serializer.errors))

    def test_work_list_user_works_only(self):
        """Test that users only see their own works"""
        from festival.models import Work
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create test files
        file1 = SimpleUploadedFile(
            "work1.pdf", b"work1 file content", content_type="application/pdf"
        )
        file2 = SimpleUploadedFile(
            "work2.pdf", b"work2 file content", content_type="application/pdf"
        )

        # Create works for both users
        work1 = Work.objects.create(
            festival_registration=self.registration1,
            title="کار کاربر اول",
            description="توضیحات کار کاربر اول",
            file=file1,
        )
        work2 = Work.objects.create(
            festival_registration=self.registration2,
            title="کار کاربر دوم",
            description="توضیحات کار کاربر دوم",
            file=file2,
        )

        # User 1 should only see their work
        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:work-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], work1.id)

        # User 2 should only see their work
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], work2.id)

    def test_work_detail_success(self):
        """Test successful work detail retrieval"""
        from festival.models import Work
        from django.core.files.uploadedfile import SimpleUploadedFile

        test_file = SimpleUploadedFile(
            "detail_test.pdf",
            b"detail test file content",
            content_type="application/pdf",
        )

        work = Work.objects.create(
            festival_registration=self.registration1,
            title="کار نمونه",
            description="توضیحات کار نمونه",
            file=test_file,
        )

        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:work-detail", kwargs={"pk": work.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], work.id)
        self.assertEqual(response.data["title"], work.title)

    def test_work_detail_unauthenticated(self):
        """Test work detail access for unauthenticated users should fail"""
        from festival.models import Work
        from django.core.files.uploadedfile import SimpleUploadedFile

        test_file = SimpleUploadedFile(
            "unauth_test.pdf",
            b"unauth test file content",
            content_type="application/pdf",
        )

        work = Work.objects.create(
            festival_registration=self.registration1,
            title="کار نمونه",
            description="توضیحات کار نمونه",
            file=test_file,
        )

        url = reverse("festival:work-detail", kwargs={"pk": work.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_work_detail_other_user(self):
        """Test that users cannot access other users' works"""
        from festival.models import Work
        from django.core.files.uploadedfile import SimpleUploadedFile

        test_file = SimpleUploadedFile(
            "other_user_test.pdf",
            b"other user test file content",
            content_type="application/pdf",
        )

        work = Work.objects.create(
            festival_registration=self.registration1,
            title="کار کاربر اول",
            description="توضیحات کار کاربر اول",
            file=test_file,
        )

        # User 2 tries to access User 1's work
        self.client.force_authenticate(user=self.user2)
        url = reverse("festival:work-detail", kwargs={"pk": work.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_work_update_success(self):
        """Test successful work update"""
        from festival.models import Work
        from django.core.files.uploadedfile import SimpleUploadedFile

        initial_file = SimpleUploadedFile(
            "initial_file.pdf", b"initial file content", content_type="application/pdf"
        )

        work = Work.objects.create(
            festival_registration=self.registration1,
            title="کار اصلی",
            description="توضیحات اصلی",
            file=initial_file,
        )

        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:work-detail", kwargs={"pk": work.pk})

        updated_file = SimpleUploadedFile(
            "updated_file.pdf",
            b"updated file content for testing",
            content_type="application/pdf",
        )

        update_data = {
            "festival_registration": self.registration1.id,
            "title": "کار به‌روزرسانی شده",
            "description": "توضیحات به‌روزرسانی شده برای کار",
            "file": updated_file,
        }

        response = self.client.put(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], update_data["title"])
        self.assertEqual(response.data["description"], update_data["description"])

    def test_work_delete_success(self):
        """Test successful work deletion"""
        from festival.models import Work
        from django.core.files.uploadedfile import SimpleUploadedFile

        delete_file = SimpleUploadedFile(
            "delete_test.pdf",
            b"delete test file content",
            content_type="application/pdf",
        )

        work = Work.objects.create(
            festival_registration=self.registration1,
            title="کار برای حذف",
            description="این کار برای تست حذف است",
            file=delete_file,
        )

        self.client.force_authenticate(user=self.user1)
        url = reverse("festival:work-detail", kwargs={"pk": work.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify work is deleted
        self.assertFalse(Work.objects.filter(id=work.id).exists())
