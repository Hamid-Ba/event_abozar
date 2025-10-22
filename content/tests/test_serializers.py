"""
Content Serializers Tests
Testing serializer validation for Education video and document fields
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError
from content.serializers import EducationSerializer


class EducationSerializerTest(TestCase):
    """Test cases for Education serializer validation"""

    def test_valid_video_upload(self):
        """Test that valid video file passes validation"""
        valid_video = SimpleUploadedFile(
            "tutorial.mp4", b"fake video content", content_type="video/mp4"
        )

        serializer = EducationSerializer()
        result = serializer.validate_video(valid_video)

        self.assertEqual(result, valid_video)

    def test_video_too_large(self):
        """Test that oversized video file fails validation"""
        # Create a file larger than 500MB
        large_video = SimpleUploadedFile(
            "huge_video.mp4",
            b"x" * (501 * 1024 * 1024),  # 501 MB
            content_type="video/mp4",
        )

        serializer = EducationSerializer()

        with self.assertRaises(ValidationError) as context:
            serializer.validate_video(large_video)

        error_message = str(context.exception.detail[0])
        self.assertIn("500", error_message)
        self.assertIn("مگابایت", error_message)

    def test_video_invalid_format(self):
        """Test that invalid video format fails validation"""
        invalid_video = SimpleUploadedFile(
            "video.webm", b"fake content", content_type="video/webm"
        )

        serializer = EducationSerializer()

        with self.assertRaises(ValidationError) as context:
            serializer.validate_video(invalid_video)

        error_message = str(context.exception.detail[0])
        self.assertIn("فرمت", error_message)

    def test_video_none_allowed(self):
        """Test that None value is allowed for optional video field"""
        serializer = EducationSerializer()
        result = serializer.validate_video(None)

        self.assertIsNone(result)

    def test_valid_document_upload(self):
        """Test that valid document file passes validation"""
        valid_document = SimpleUploadedFile(
            "slides.pdf", b"fake pdf content", content_type="application/pdf"
        )

        serializer = EducationSerializer()
        result = serializer.validate_document(valid_document)

        self.assertEqual(result, valid_document)

    def test_document_too_large(self):
        """Test that oversized document file fails validation"""
        # Create a file larger than 50MB
        large_document = SimpleUploadedFile(
            "huge_presentation.pdf",
            b"x" * (51 * 1024 * 1024),  # 51 MB
            content_type="application/pdf",
        )

        serializer = EducationSerializer()

        with self.assertRaises(ValidationError) as context:
            serializer.validate_document(large_document)

        error_message = str(context.exception.detail[0])
        self.assertIn("50", error_message)
        self.assertIn("مگابایت", error_message)

    def test_document_invalid_format(self):
        """Test that invalid document format fails validation"""
        invalid_document = SimpleUploadedFile(
            "document.docx",
            b"fake content",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        serializer = EducationSerializer()

        with self.assertRaises(ValidationError) as context:
            serializer.validate_document(invalid_document)

        error_message = str(context.exception.detail[0])
        self.assertIn("فرمت", error_message)

    def test_document_none_allowed(self):
        """Test that None value is allowed for optional document field"""
        serializer = EducationSerializer()
        result = serializer.validate_document(None)

        self.assertIsNone(result)

    def test_all_video_formats_accepted(self):
        """Test that all allowed video formats are accepted"""
        allowed_formats = [
            ("video.mp4", "video/mp4"),
            ("video.avi", "video/x-msvideo"),
            ("video.mov", "video/quicktime"),
            ("video.mkv", "video/x-matroska"),
            ("video.wmv", "video/x-ms-wmv"),
        ]

        serializer = EducationSerializer()

        for filename, content_type in allowed_formats:
            video = SimpleUploadedFile(
                filename, b"fake video content", content_type=content_type
            )

            result = serializer.validate_video(video)
            self.assertEqual(result, video)

    def test_all_document_formats_accepted(self):
        """Test that all allowed document formats are accepted"""
        allowed_formats = [
            ("doc.pdf", "application/pdf"),
            ("presentation.ppt", "application/vnd.ms-powerpoint"),
            (
                "slides.pptx",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ),
        ]

        serializer = EducationSerializer()

        for filename, content_type in allowed_formats:
            document = SimpleUploadedFile(
                filename, b"fake document content", content_type=content_type
            )

            result = serializer.validate_document(document)
            self.assertEqual(result, document)
