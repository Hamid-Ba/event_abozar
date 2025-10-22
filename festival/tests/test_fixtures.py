"""
Test Fixtures and Utilities for Festival Module
"""
from django.contrib.auth import get_user_model
from festival.models import (
    FestivalRegistration,
    FestivalFormat,
    FestivalTopic,
    FestivalSpecialSection,
)
from province.models import Province, City

User = get_user_model()


# Test data fixtures
TEST_PROVINCES = [
    {"name": "تهران", "slug": "tehran"},
    {"name": "اصفهان", "slug": "isfahan"},
    {"name": "فارس", "slug": "fars"},
    {"name": "خراسان رضوی", "slug": "khorasan-razavi"},
    {"name": "خوزستان", "slug": "khuzestan"},
]

TEST_CITIES = [
    {"name": "تهران", "slug": "tehran-city", "province_slug": "tehran"},
    {"name": "کرج", "slug": "karaj", "province_slug": "tehran"},
    {"name": "ری", "slug": "rey", "province_slug": "tehran"},
    {"name": "اصفهان", "slug": "isfahan-city", "province_slug": "isfahan"},
    {"name": "کاشان", "slug": "kashan", "province_slug": "isfahan"},
    {"name": "شیراز", "slug": "shiraz", "province_slug": "fars"},
    {"name": "مشهد", "slug": "mashhad", "province_slug": "khorasan-razavi"},
    {"name": "اهواز", "slug": "ahvaz", "province_slug": "khuzestan"},
]

TEST_USERS = [
    {"phone": "09123456789", "fullName": "علی احمدی"},
    {"phone": "09987654321", "fullName": "فاطمه حسینی"},
    {"phone": "09555666777", "fullName": "محمد رضایی"},
    {"phone": "09111222333", "fullName": "مریم کریمی"},
]

# Category codes - these will be used to get the objects from migration data
TEST_REGISTRATION_CATEGORY_CODES = {
    "format_news_report": "news_report",
    "format_interview": "interview",
    "format_documentary": "documentary",
    "topic_year_slogan": "year_slogan",
    "topic_media_industry": "media_industry",
    "topic_revolution": "revolution_achievements",
    "section_progress": "progress_narrative",
    "section_field": "field_narrative_12days",
}


def get_category_objects():
    """Get or create category objects for tests"""
    return {
        "format_news_report": FestivalFormat.objects.get(code="news_report"),
        "format_interview": FestivalFormat.objects.get(code="interview"),
        "format_documentary": FestivalFormat.objects.get(code="documentary"),
        "topic_year_slogan": FestivalTopic.objects.get(code="year_slogan"),
        "topic_media_industry": FestivalTopic.objects.get(code="media_industry"),
        "topic_revolution": FestivalTopic.objects.get(code="revolution_achievements"),
        "section_progress": FestivalSpecialSection.objects.get(
            code="progress_narrative"
        ),
        "section_field": FestivalSpecialSection.objects.get(
            code="field_narrative_12days"
        ),
    }


# Updated TEST_REGISTRATIONS - will use category objects
def get_test_registration_data(categories):
    """Get test registration data with proper category objects"""
    return [
        {
            "full_name": "علی احمدی",
            "father_name": "محمد",
            "national_id": "1234567890",
            "gender": "male",
            "education": "کارشناسی",
            "phone_number": "09123456789",
            "virtual_number": "@ali_ahmadi",
            "media_name": "رسانه آزاد",
            "festival_format": categories["format_news_report"],
            "festival_topic": categories["topic_year_slogan"],
            "special_section": categories["section_progress"],
        },
        {
            "full_name": "فاطمه حسینی",
            "father_name": "علی",
            "national_id": "0987654321",
            "gender": "female",
            "education": "کارشناسی ارشد",
            "phone_number": "09987654321",
            "virtual_number": "@fatemeh_h",
            "media_name": "رسانه ملی",
            "festival_format": categories["format_interview"],
            "festival_topic": categories["topic_media_industry"],
            "special_section": None,
        },
        {
            "full_name": "محمد رضایی",
            "father_name": "حسن",
            "national_id": "1122334455",
            "gender": "male",
            "education": "دکتری",
            "phone_number": "09555666777",
            "virtual_number": "@mohammad_r",
            "media_name": "رسانه جوان",
            "festival_format": categories["format_documentary"],
            "festival_topic": categories["topic_revolution"],
            "special_section": categories["section_field"],
        },
    ]


def create_test_provinces():
    """Create test provinces"""
    provinces = []
    for province_data in TEST_PROVINCES:
        province, created = Province.objects.get_or_create(
            slug=province_data["slug"], defaults={"name": province_data["name"]}
        )
        provinces.append(province)
    return provinces


def create_test_cities():
    """Create test cities"""
    provinces = create_test_provinces()
    province_map = {p.slug: p for p in provinces}

    cities = []
    for city_data in TEST_CITIES:
        province = province_map[city_data["province_slug"]]
        city, created = City.objects.get_or_create(
            slug=city_data["slug"],
            defaults={"name": city_data["name"], "province": province},
        )
        cities.append(city)
    return cities


def create_test_users():
    """Create test users"""
    users = []
    for user_data in TEST_USERS:
        user, created = User.objects.get_or_create(
            phone=user_data["phone"], defaults={"fullName": user_data["fullName"]}
        )
        users.append(user)
    return users


def create_test_registrations():
    """Create test registrations"""
    provinces = create_test_provinces()
    cities = create_test_cities()
    users = create_test_users()
    categories = get_category_objects()
    test_registrations = get_test_registration_data(categories)

    # Map cities to their provinces for easy lookup
    tehran_province = Province.objects.get(slug="tehran")
    isfahan_province = Province.objects.get(slug="isfahan")
    fars_province = Province.objects.get(slug="fars")

    tehran_city = City.objects.get(slug="tehran-city")
    isfahan_city = City.objects.get(slug="isfahan-city")
    shiraz_city = City.objects.get(slug="shiraz")

    registrations = []
    for i, registration_data in enumerate(test_registrations):
        user = users[i]

        # Assign provinces and cities
        if i == 0:
            province, city = tehran_province, tehran_city
        elif i == 1:
            province, city = isfahan_province, isfahan_city
        else:
            province, city = fars_province, shiraz_city

        registration, created = FestivalRegistration.objects.get_or_create(
            national_id=registration_data["national_id"],
            defaults={
                "user": user,
                "province": province,
                "city": city,
                **registration_data,
            },
        )
        registrations.append(registration)

    return registrations


class FestivalTestMixin:
    """Mixin to provide common test data setup"""

    def setUp(self):
        """Set up common test data"""
        super().setUp()
        self.provinces = create_test_provinces()
        self.cities = create_test_cities()
        self.users = create_test_users()
        self.categories = get_category_objects()

        # Commonly used test objects
        self.test_province = self.provinces[0]  # Tehran
        self.test_city = self.cities[0]  # Tehran city
        self.test_user = self.users[0]  # Ali Ahmadi

    def create_sample_registration(self, **overrides):
        """Create a sample registration with optional overrides"""
        defaults = {
            "user": self.test_user,
            "full_name": "علی احمدی",
            "father_name": "محمد",
            "national_id": "1234567890",
            "gender": "male",
            "education": "کارشناسی",
            "phone_number": "09123456789",
            "province": self.test_province,
            "city": self.test_city,
            "media_name": "رسانه تست",
            "festival_format": self.categories["format_news_report"],
            "festival_topic": self.categories["topic_year_slogan"],
        }
        defaults.update(overrides)
        return FestivalRegistration.objects.create(**defaults)
