"""
Work Models for Festival Registration
"""
import os
import uuid
from django.db import models
from django.utils import timezone
from .festival_registration import FestivalRegistration


def work_file_upload_path(instance, filename):
    """
    Generate unique file path for work uploads
    Format: festival/works/YYYY/MM/DD/user_id/unique_name.ext
    """
    # Get file extension
    ext = filename.split(".")[-1].lower() if "." in filename else ""

    # Generate unique filename
    unique_name = f"{uuid.uuid4().hex}"
    if ext:
        unique_name = f"{unique_name}.{ext}"

    # Create date-based directory structure
    now = timezone.now()
    date_path = now.strftime("%Y/%m/%d")

    # Include user ID for better organization
    user_id = instance.festival_registration.user.id

    return f"festival/works/{date_path}/user_{user_id}/{unique_name}"


class Work(models.Model):
    """
    Work model for festival submissions
    One-to-many relationship with FestivalRegistration
    """

    festival_registration = models.ForeignKey(
        FestivalRegistration,
        on_delete=models.CASCADE,
        related_name="works",
        verbose_name="ثبت نام جشنواره",
    )
    title = models.CharField(
        max_length=255, verbose_name="عنوان", help_text="عنوان اثر"
    )
    description = models.TextField(
        verbose_name="توضیحات", help_text="توضیحات کامل در مورد اثر"
    )
    file = models.FileField(
        upload_to=work_file_upload_path,
        verbose_name="فایل",
        help_text="فایل مربوط به اثر (حداکثر ۱۱۰ مگابایت)",
    )
    publish_link = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="لینک انتشار",
        help_text="لینک اثر منتشر شده (اختیاری)",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        verbose_name = "اثر"
        verbose_name_plural = "آثار"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.festival_registration.full_name}"

    @property
    def file_display_name(self):
        """Get a display-friendly name for the file"""
        if self.file:
            # Extract the unique filename
            unique_name = (
                self.file.name.split("/")[-1]
                if "/" in self.file.name
                else self.file.name
            )
            # Get extension
            ext = unique_name.split(".")[-1] if "." in unique_name else ""
            # Create display name from title + extension
            safe_title = "".join(
                c for c in self.title if c.isalnum() or c in (" ", "-", "_")
            ).strip()[:30]
            if ext:
                return f"{safe_title}.{ext}"
            return safe_title
        return None

    @property
    def unique_filename(self):
        """Get the unique filename without path"""
        if self.file:
            return (
                self.file.name.split("/")[-1]
                if "/" in self.file.name
                else self.file.name
            )
        return None
