"""
Province and City Integration Tests
"""
import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from province.models import Province, City


class ProvinceAPITest(APITestCase):
    """Test cases for Province API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.province1 = Province.objects.create(name="تهران", slug="tehran")
        self.province2 = Province.objects.create(name="اصفهان", slug="isfahan")
        self.province3 = Province.objects.create(name="فارس", slug="fars")

    def test_list_provinces(self):
        """Test listing all provinces"""
        url = reverse("festival:province-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        # Check that provinces are ordered by name
        province_names = [province["name"] for province in response.data]
        self.assertEqual(province_names, sorted(province_names))

    def test_province_serialization(self):
        """Test province serialization format"""
        url = reverse("festival:province-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response structure
        for province in response.data:
            self.assertIn("id", province)
            self.assertIn("name", province)
            self.assertEqual(len(province.keys()), 2)

    def test_provinces_no_authentication_required(self):
        """Test that provinces endpoint doesn't require authentication"""
        url = reverse("festival:province-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CityAPITest(APITestCase):
    """Test cases for City API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.province1 = Province.objects.create(name="تهران", slug="tehran")
        self.province2 = Province.objects.create(name="اصفهان", slug="isfahan")

        # Cities in Tehran province
        self.city1 = City.objects.create(
            name="تهران", slug="tehran-city", province=self.province1
        )
        self.city2 = City.objects.create(
            name="کرج", slug="karaj", province=self.province1
        )

        # Cities in Isfahan province
        self.city3 = City.objects.create(
            name="اصفهان", slug="isfahan-city", province=self.province2
        )
        self.city4 = City.objects.create(
            name="کاشان", slug="kashan", province=self.province2
        )

    def test_list_cities_by_province(self):
        """Test listing cities by province"""
        url = reverse("festival:city-list")
        response = self.client.get(url + f"?province_id={self.province1.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Check that returned cities belong to the correct province
        city_names = [city["name"] for city in response.data]
        self.assertIn("تهران", city_names)
        self.assertIn("کرج", city_names)

    def test_list_cities_different_province(self):
        """Test listing cities for different province"""
        url = reverse("festival:city-list")
        response = self.client.get(url + f"?province_id={self.province2.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Check that returned cities belong to the correct province
        city_names = [city["name"] for city in response.data]
        self.assertIn("اصفهان", city_names)
        self.assertIn("کاشان", city_names)

    def test_list_cities_without_province_id(self):
        """Test listing cities without providing province_id"""
        url = reverse("festival:city-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "لطفاً شناسه استان را وارد کنید")

    def test_list_cities_invalid_province_id(self):
        """Test listing cities with invalid province_id"""
        url = reverse("festival:city-list")
        response = self.client.get(url + "?province_id=9999")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No cities for non-existent province

    def test_list_cities_non_numeric_province_id(self):
        """Test listing cities with non-numeric province_id"""
        url = reverse("festival:city-list")
        # Non-numeric province_id should return 400 error or handle gracefully
        response = self.client.get(url + "?province_id=invalid")

        # The view should handle this gracefully and return 400 or empty list
        self.assertIn(
            response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK]
        )
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(len(response.data), 0)  # No cities found

    def test_city_serialization(self):
        """Test city serialization format"""
        url = reverse("festival:city-list")
        response = self.client.get(url + f"?province_id={self.province1.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response structure
        for city in response.data:
            self.assertIn("id", city)
            self.assertIn("name", city)
            self.assertEqual(len(city.keys()), 2)

    def test_cities_ordering(self):
        """Test that cities are ordered by name"""
        url = reverse("festival:city-list")
        response = self.client.get(url + f"?province_id={self.province1.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that cities are ordered by name
        city_names = [city["name"] for city in response.data]
        self.assertEqual(city_names, sorted(city_names))

    def test_cities_no_authentication_required(self):
        """Test that cities endpoint doesn't require authentication"""
        url = reverse("festival:city-list")
        response = self.client.get(url + f"?province_id={self.province1.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProvinceAndCityIntegrationTest(APITestCase):
    """Integration tests for province and city functionality with festival registration"""

    def setUp(self):
        """Set up test data"""
        self.province = Province.objects.create(name="تهران", slug="tehran")
        self.city = City.objects.create(
            name="تهران", slug="tehran-city", province=self.province
        )

        self.other_province = Province.objects.create(name="اصفهان", slug="isfahan")

    def test_province_city_workflow(self):
        """Test complete workflow of getting provinces, then cities, then creating registration"""
        # Step 1: Get provinces
        provinces_url = reverse("festival:province-list")
        provinces_response = self.client.get(provinces_url)

        self.assertEqual(provinces_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(provinces_response.data), 0)

        # Step 2: Get cities for first province
        province_id = provinces_response.data[0]["id"]
        cities_url = reverse("festival:city-list")
        cities_response = self.client.get(cities_url + f"?province_id={province_id}")

        self.assertEqual(cities_response.status_code, status.HTTP_200_OK)

        # If there are cities, test registration creation
        if len(cities_response.data) > 0:
            city_id = cities_response.data[0]["id"]

            # Step 3: Create registration using province and city IDs
            registration_data = {
                "full_name": "علی احمدی",
                "father_name": "محمد",
                "national_id": "1234567890",
                "gender": "male",
                "education": "کارشناسی",
                "phone_number": "09123456789",
                "province_id": province_id,
                "city_id": city_id,
                "media_name": "رسانه تست",
                "festival_format": "news_report",
                "festival_topic": "year_slogan",
            }

            registration_url = reverse("festival:registration-create")
            registration_response = self.client.post(
                registration_url,
                data=json.dumps(registration_data),
                content_type="application/json",
            )

            self.assertEqual(registration_response.status_code, status.HTTP_201_CREATED)

    def test_invalid_province_city_combination(self):
        """Test registration creation with invalid province-city combination"""
        # Create a city that doesn't belong to the province
        other_city = City.objects.create(
            name="اصفهان", slug="isfahan-city", province=self.other_province
        )

        registration_data = {
            "full_name": "علی احمدی",
            "father_name": "محمد",
            "national_id": "1234567890",
            "gender": "male",
            "education": "کارشناسی",
            "phone_number": "09123456789",
            "province_id": self.province.id,  # Tehran province
            "city_id": other_city.id,  # Isfahan city (mismatch)
            "media_name": "رسانه تست",
            "festival_format": "news_report",
            "festival_topic": "year_slogan",
        }

        registration_url = reverse("festival:registration-create")
        response = self.client.post(
            registration_url,
            data=json.dumps(registration_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_list_with_province_city_info(self):
        """Test that registration list includes province and city information"""
        from festival.models import (
            FestivalRegistration,
            FestivalFormat,
            FestivalTopic,
            FestivalSpecialSection,
        )
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create(phone="09123456789")

        # Create a registration
        registration = FestivalRegistration.objects.create(
            user=user,
            full_name="علی احمدی",
            father_name="محمد",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست",
            festival_format=FestivalFormat.objects.get(code="news_report"),
            festival_topic=FestivalTopic.objects.get(code="year_slogan"),
        )

        # Get registration list
        list_url = reverse("festival:registration-list")
        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Check that province and city info is included
        registration_data = response.data[0]
        self.assertIn("province_name", registration_data)
        self.assertIn("city_name", registration_data)
        self.assertEqual(registration_data["province_name"], "تهران")
        self.assertEqual(registration_data["city_name"], "تهران")

    def test_registration_detail_with_province_city_info(self):
        """Test that registration detail includes full province and city objects"""
        from festival.models import (
            FestivalRegistration,
            FestivalFormat,
            FestivalTopic,
            FestivalSpecialSection,
        )
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create(phone="09123456789")

        # Create a registration
        registration = FestivalRegistration.objects.create(
            user=user,
            full_name="علی احمدی",
            father_name="محمد",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09123456789",
            province=self.province,
            city=self.city,
            media_name="رسانه تست",
            festival_format=FestivalFormat.objects.get(code="news_report"),
            festival_topic=FestivalTopic.objects.get(code="year_slogan"),
        )

        # Get registration detail
        detail_url = reverse(
            "festival:registration-detail", kwargs={"id": registration.id}
        )
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that full province and city objects are included
        registration_data = response.data
        self.assertIn("province", registration_data)
        self.assertIn("city", registration_data)

        self.assertEqual(registration_data["province"]["id"], self.province.id)
        self.assertEqual(registration_data["province"]["name"], "تهران")
        self.assertEqual(registration_data["city"]["id"], self.city.id)
        self.assertEqual(registration_data["city"]["name"], "تهران")
