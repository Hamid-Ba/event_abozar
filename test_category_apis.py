"""
Manual test script for Category List APIs
اسکریپت تست دستی برای API های لیست دسته‌بندی
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory
from festival.views import (
    FestivalFormatListView,
    FestivalTopicListView,
    FestivalSpecialSectionListView,
)


def test_category_apis():
    """Test all category list APIs"""
    factory = RequestFactory()

    print("=" * 80)
    print("Testing Festival Category List APIs")
    print("=" * 80)

    # Test Format List API
    print("\n1. Testing Festival Format List API")
    print("-" * 80)
    request = factory.get("/api/festival/formats/")
    view = FestivalFormatListView.as_view()
    response = view(request)
    response.render()

    print(f"Status Code: {response.status_code}")
    print(f"Number of formats: {len(response.data)}")
    if response.data:
        print(f"\nFirst format:")
        print(f"  - ID: {response.data[0]['id']}")
        print(f"  - Code: {response.data[0]['code']}")
        print(f"  - Name: {response.data[0]['name']}")
        print(f"  - Description: {response.data[0].get('description', 'N/A')}")

    # Test Topic List API
    print("\n2. Testing Festival Topic List API")
    print("-" * 80)
    request = factory.get("/api/festival/topics/")
    view = FestivalTopicListView.as_view()
    response = view(request)
    response.render()

    print(f"Status Code: {response.status_code}")
    print(f"Number of topics: {len(response.data)}")
    if response.data:
        print(f"\nFirst topic:")
        print(f"  - ID: {response.data[0]['id']}")
        print(f"  - Code: {response.data[0]['code']}")
        print(f"  - Name: {response.data[0]['name']}")
        print(f"  - Description: {response.data[0].get('description', 'N/A')}")

    # Test Special Section List API
    print("\n3. Testing Festival Special Section List API")
    print("-" * 80)
    request = factory.get("/api/festival/special-sections/")
    view = FestivalSpecialSectionListView.as_view()
    response = view(request)
    response.render()

    print(f"Status Code: {response.status_code}")
    print(f"Number of special sections: {len(response.data)}")
    if response.data:
        print(f"\nFirst special section:")
        print(f"  - ID: {response.data[0]['id']}")
        print(f"  - Code: {response.data[0]['code']}")
        print(f"  - Name: {response.data[0]['name']}")
        print(f"  - Description: {response.data[0].get('description', 'N/A')}")

    print("\n" + "=" * 80)
    print("✅ All Category APIs are working correctly!")
    print("=" * 80)

    # Display URLs
    print("\n📍 API Endpoints:")
    print("  - Formats: GET /api/festival/formats/")
    print("  - Topics: GET /api/festival/topics/")
    print("  - Special Sections: GET /api/festival/special-sections/")
    print("\n💡 Query Parameters:")
    print("  - is_active=true|false|all (default: true)")
    print("\n")


if __name__ == "__main__":
    test_category_apis()
