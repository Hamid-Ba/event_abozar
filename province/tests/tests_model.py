"""
Test Province Module
"""
from django.test import TestCase
from province.models import Province, City

from django.template.defaultfilters import slugify


def create_province(name, slug):
    """Helper Function To Create Province"""
    return Province.objects.create(name=name, slug=slug)


class ProvinceTest(TestCase):
    """Test Province Model"""

    def test_create_province_should_work_propely(self):
        """Test To Create Province Object"""
        name = "tehran"
        slug = slugify(name)
        province = Province.objects.create(name=name, slug=slug)
        self.assertEqual(province.name, name)


class CityTest(TestCase):
    """Test City Model"""

    def test_create_city_should_work_propely(self):
        """Test To Create City Object"""
        province = create_province(
            name="sistan va baluchestan", slug=slugify("sistan va baluchestan")
        )
        city_name = "zahedan"
        slug = slugify(city_name)
        city = City.objects.create(name=city_name, slug=slug, province=province)

        self.assertEqual(city.name, city_name)
        self.assertEqual(city.province.name, province.name)
