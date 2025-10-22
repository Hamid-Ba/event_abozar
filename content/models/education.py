"""
Education Model
Model for managing educational content
"""
import os
import uuid
from django.db import models
from .base import BaseContentModel


def education_video_upload_path(instance, filename):
    """
    Generate random upload path for education videos
    Format: content/education/videos/<random_uuid>.<extension>
    """
    ext = os.path.splitext(filename)[1].lower()  # Get file extension
    random_filename = f"{uuid.uuid4().hex}{ext}"
    return f"content/education/videos/{random_filename}"


def education_document_upload_path(instance, filename):
    """
    Generate random upload path for education documents
    Format: content/education/documents/<random_uuid>.<extension>
    """
    ext = os.path.splitext(filename)[1].lower()  # Get file extension
    random_filename = f"{uuid.uuid4().hex}{ext}"
    return f"content/education/documents/{random_filename}"


class Education(BaseContentModel):
    """
    Education model for managing educational content with video and document support
    """

    video = models.FileField(
        upload_to=education_video_upload_path,
        blank=True,
        null=True,
        verbose_name="ویدیو آموزشی",
        help_text="فایل ویدیوی آموزشی (فرمت‌های مجاز: mp4, avi, mov, mkv, wmv - حداکثر 500 مگابایت)",
    )

    document = models.FileField(
        upload_to=education_document_upload_path,
        blank=True,
        null=True,
        verbose_name="فایل آموزشی",
        help_text="فایل آموزشی PDF یا PowerPoint (فرمت‌های مجاز: pdf, ppt, pptx - حداکثر 50 مگابایت)",
    )

    class Meta:
        verbose_name = "آموزش"
        verbose_name_plural = "آموزش‌ها"
        ordering = ["-publish_date"]

    @property
    def has_video(self):
        """Check if education has video"""
        return bool(self.video)

    @property
    def has_document(self):
        """Check if education has document"""
        return bool(self.document)

    @property
    def video_filename(self):
        """Get video filename"""
        if self.video:
            return self.video.name.split("/")[-1]
        return None

    @property
    def document_filename(self):
        """Get document filename"""
        if self.document:
            return self.document.name.split("/")[-1]
        return None
