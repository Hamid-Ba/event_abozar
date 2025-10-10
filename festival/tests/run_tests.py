"""
Festival Module Test Runner

This script provides easy commands to run different test suites for the festival module.

Usage:
    python manage.py test festival.tests  # Run all festival tests
    python manage.py test festival.tests.test_models  # Run only model tests
    python manage.py test festival.tests.test_api  # Run only API tests
    python manage.py test festival.tests.test_province_city  # Run only province/city tests
    python manage.py test festival.tests.test_services  # Run only service tests

Coverage (if coverage.py is installed):
    coverage run --source='festival' manage.py test festival.tests
    coverage report
    coverage html
"""

import sys
import os
from django.test import TestCase


class FestivalTestSuite:
    """Test suite information for festival module"""

    TEST_MODULES = [
        "festival.tests.test_models",
        "festival.tests.test_api",
        "festival.tests.test_province_city",
        "festival.tests.test_services",
    ]

    @classmethod
    def get_test_info(cls):
        """Get information about available tests"""
        info = {
            "total_modules": len(cls.TEST_MODULES),
            "modules": {
                "test_models": {
                    "description": "Model validation, relationships, and database constraints",
                    "test_classes": ["FestivalRegistrationModelTest"],
                    "key_tests": [
                        "test_create_festival_registration_success",
                        "test_unique_national_id_constraint",
                        "test_foreign_key_relationships",
                        "test_choice_field_validation",
                    ],
                },
                "test_api": {
                    "description": "API endpoints, serialization, and HTTP responses",
                    "test_classes": ["FestivalRegistrationAPITest"],
                    "key_tests": [
                        "test_create_registration_success",
                        "test_list_registrations_with_filters",
                        "test_search_registration_by_phone",
                        "test_create_registration_city_province_mismatch",
                    ],
                },
                "test_province_city": {
                    "description": "Province and city integration with festival registration",
                    "test_classes": [
                        "ProvinceAPITest",
                        "CityAPITest",
                        "ProvinceAndCityIntegrationTest",
                    ],
                    "key_tests": [
                        "test_list_provinces",
                        "test_list_cities_by_province",
                        "test_province_city_workflow",
                        "test_invalid_province_city_combination",
                    ],
                },
                "test_services": {
                    "description": "Service layer logic, user creation, and business rules",
                    "test_classes": ["FestivalServicesTest"],
                    "key_tests": [
                        "test_create_festival_registration_new_user",
                        "test_create_festival_registration_existing_user",
                        "test_create_festival_registration_transaction_rollback",
                        "test_create_festival_registration_concurrent_access",
                    ],
                },
            },
        }
        return info

    @classmethod
    def print_test_info(cls):
        """Print test suite information"""
        info = cls.get_test_info()

        print("=" * 80)
        print("🎭 FESTIVAL MODULE TEST SUITE")
        print("=" * 80)
        print(f"Total test modules: {info['total_modules']}")
        print()

        for module_name, module_info in info["modules"].items():
            print(f"📋 {module_name.upper()}")
            print(f"   Description: {module_info['description']}")
            print(f"   Test Classes: {', '.join(module_info['test_classes'])}")
            print(f"   Key Tests:")
            for test in module_info["key_tests"]:
                print(f"     • {test}")
            print()

        print("🚀 RUNNING TESTS:")
        print("   python manage.py test festival.tests")
        print("   python manage.py test festival.tests.test_models")
        print("   python manage.py test festival.tests.test_api")
        print("   python manage.py test festival.tests.test_province_city")
        print("   python manage.py test festival.tests.test_services")
        print()

        print("📊 COVERAGE (install coverage.py first):")
        print("   pip install coverage")
        print("   coverage run --source='festival' manage.py test festival.tests")
        print("   coverage report")
        print("   coverage html")
        print("=" * 80)


if __name__ == "__main__":
    FestivalTestSuite.print_test_info()
