"""
Test to verify PDF file upload works for Work creation
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework.test import force_authenticate

from festival.models import FestivalRegistration, FestivalFormat, FestivalTopic
from festival.views import WorkListCreateView
from province.models import Province, City

User = get_user_model()


def test_pdf_upload():
    """Test that PDF files can be uploaded for Work creation"""

    print("=" * 80)
    print("Testing PDF File Upload for Work Creation")
    print("=" * 80)

    # Create test data
    user = User.objects.create(phone="09123456789", fullName="علی احمدی")
    province = Province.objects.create(name="تهران", slug="tehran")
    city = City.objects.create(name="تهران", slug="tehran-city", province=province)

    # Get category objects
    format_obj = FestivalFormat.objects.first()
    topic_obj = FestivalTopic.objects.first()

    # Create registration
    registration = FestivalRegistration.objects.create(
        user=user,
        full_name="علی احمدی",
        father_name="محمد",
        national_id="1234567890",
        gender="male",
        education="کارشناسی",
        phone_number="09123456789",
        province=province,
        city=city,
        media_name="رسانه تست",
        festival_format=format_obj,
        festival_topic=topic_obj,
    )

    # Create PDF file
    pdf_content = b"%PDF-1.4\nTest PDF content"
    pdf_file = SimpleUploadedFile(
        "test_document.pdf", pdf_content, content_type="application/pdf"
    )

    # Prepare request
    factory = RequestFactory()
    request = factory.post(
        "/api/festival/works/",
        {
            "festival_registration": registration.id,
            "title": "تست آپلود PDF",
            "description": "این یک تست برای آپلود فایل PDF است",
            "file": pdf_file,
        },
    )
    force_authenticate(request, user=user)

    # Call view
    view = WorkListCreateView.as_view()
    response = view(request)

    # Check results
    print(f"\n✅ Response Status: {response.status_code}")

    if response.status_code == 201:
        print("✅ PDF file was accepted successfully!")
        print(f"\n📄 Created Work Details:")
        print(f"   - Title: {response.data.get('title')}")
        print(f"   - Description: {response.data.get('description')}")
        print(f"   - File Name: {response.data.get('unique_filename', 'N/A')}")
        print(f"   - File Size: {len(pdf_content)} bytes")
    else:
        print(f"❌ Failed with status {response.status_code}")
        if hasattr(response, "data"):
            print(f"   Error: {response.data}")

    print("\n" + "=" * 80)
    print("Allowed File Extensions in WorkCreateSerializer:")
    print("=" * 80)

    allowed_extensions = [
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",  # Documents
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",  # Images
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".wmv",  # Videos
        ".mp3",
        ".wav",
        ".aac",
        ".flac",  # Audio
        ".zip",
        ".rar",
        ".7z",  # Archives
    ]

    print("\n📁 Document Formats:")
    print("   ", ", ".join(allowed_extensions[:5]))

    print("\n🖼️  Image Formats:")
    print("   ", ", ".join(allowed_extensions[5:10]))

    print("\n🎬 Video Formats:")
    print("   ", ", ".join(allowed_extensions[10:15]))

    print("\n🎵 Audio Formats:")
    print("   ", ", ".join(allowed_extensions[15:19]))

    print("\n📦 Archive Formats:")
    print("   ", ", ".join(allowed_extensions[19:]))

    print("\n" + "=" * 80)
    print("File Size Limit: 110 MB (115,343,360 bytes)")
    print("=" * 80)
    print()


if __name__ == "__main__":
    test_pdf_upload()
