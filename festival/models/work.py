"""
Work Models for Festival Registration
"""
import os
import uuid
from django.db import models
from django.utils import timezone
from .festival_registration import FestivalRegistration
from .categories import FestivalFormat, FestivalTopic, FestivalSpecialSection


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


def work_file_item_upload_path(instance, filename):
    """مسیر یکتا برای هر فایل اثر: festival/works/YYYY/MM/DD/user_<id>/<uuid>.<ext>"""
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    unique_name = uuid.uuid4().hex
    if ext:
        unique_name = f"{unique_name}.{ext}"
    date_path = timezone.now().strftime("%Y/%m/%d")
    user_id = instance.work.festival_registration.user_id
    return f"festival/works/{date_path}/user_{user_id}/{unique_name}"


class Work(models.Model):
    """
    Work model for festival submissions
    One-to-many relationship with FestivalRegistration
    """

    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STATUS_UNDER_REVIEW = "under_review"
    STATUS_JUDGED = "judged"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "پیش‌نویس (بدون فایل)"),
        (STATUS_SUBMITTED, "ارسال‌شده"),
        (STATUS_UNDER_REVIEW, "در حال داوری"),
        (STATUS_JUDGED, "داوری‌شده"),
    ]

    festival_registration = models.ForeignKey(
        FestivalRegistration,
        on_delete=models.CASCADE,
        related_name="works",
        verbose_name="ثبت نام جشنواره",
    )
    # قالب/محور/بخش ویژه روی خود اثر است تا یک ثبت‌نام بتواند چند اثر در موضوعات مختلف داشته باشد
    festival_format = models.ForeignKey(
        FestivalFormat,
        on_delete=models.PROTECT,
        related_name="works",
        null=True,
        blank=True,
        verbose_name="قالب",
    )
    festival_topic = models.ForeignKey(
        FestivalTopic,
        on_delete=models.PROTECT,
        related_name="works",
        null=True,
        blank=True,
        verbose_name="محور",
    )
    special_section = models.ForeignKey(
        FestivalSpecialSection,
        on_delete=models.PROTECT,
        related_name="works",
        null=True,
        blank=True,
        verbose_name="بخش ویژه",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        db_index=True,
        verbose_name="وضعیت",
    )
    final_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        verbose_name="امتیاز نهایی",
        help_text="مجموع امتیاز همهٔ داوران",
    )
    reviews_count = models.PositiveSmallIntegerField(
        default=0, editable=False, verbose_name="تعداد داوران امتیازدهنده"
    )
    title = models.CharField(
        max_length=255, verbose_name="عنوان", help_text="عنوان اثر"
    )
    description = models.TextField(
        verbose_name="توضیحات", help_text="توضیحات کامل در مورد اثر"
    )
    # منسوخ: فایل‌های اثر اکنون در WorkFile نگهداری می‌شوند. برای سازگاری با نسخه قبل می‌ماند
    file = models.FileField(
        upload_to=work_file_upload_path,
        blank=True,
        verbose_name="فایل (منسوخ)",
        help_text="منسوخ: از WorkFile استفاده کنید",
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
    def required_judges(self):
        festival = self.festival_registration.festival
        return festival.required_judges if festival else 3

    def recalculate_scores(self):
        """
        امتیاز نهایی = مجموع امتیاز داوران؛ وضعیت اثر از روی تعداد داوران:
        صفر → ارسال‌شده، کمتر از لازم → در حال داوری، به حد نصاب رسید → داوری‌شده
        """
        agg = self.reviews.aggregate(total=models.Sum("score"), n=models.Count("id"))
        count = agg["n"] or 0
        updates = {"final_score": agg["total"], "reviews_count": count}
        if self.status != self.STATUS_DRAFT:
            if count == 0:
                updates["status"] = self.STATUS_SUBMITTED
            elif count >= self.required_judges:
                updates["status"] = self.STATUS_JUDGED
            else:
                updates["status"] = self.STATUS_UNDER_REVIEW
        old_status = self.status
        Work.objects.filter(pk=self.pk).update(**updates)
        for field, value in updates.items():
            setattr(self, field, value)
        if self.status != old_status:
            from festival.notifications import notify_work_status

            notify_work_status(self)

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


class WorkFile(models.Model):
    """یک فایل از فایل‌های یک اثر (ویدیو، پادکست، PDF و ...)"""

    KIND_VIDEO = "video"
    KIND_AUDIO = "audio"
    KIND_IMAGE = "image"
    KIND_DOCUMENT = "document"
    KIND_ARCHIVE = "archive"
    KIND_CHOICES = [
        (KIND_VIDEO, "ویدیو"),
        (KIND_AUDIO, "صوت"),
        (KIND_IMAGE, "تصویر"),
        (KIND_DOCUMENT, "سند"),
        (KIND_ARCHIVE, "فایل فشرده"),
    ]

    work = models.ForeignKey(
        Work, on_delete=models.CASCADE, related_name="files", verbose_name="اثر"
    )
    file = models.FileField(upload_to=work_file_item_upload_path, verbose_name="فایل")
    original_name = models.CharField(
        max_length=255, blank=True, verbose_name="نام اصلی فایل"
    )
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, verbose_name="نوع")
    size = models.BigIntegerField(default=0, verbose_name="حجم (بایت)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "فایل اثر"
        verbose_name_plural = "فایل‌های اثر"
        ordering = ["created_at", "id"]

    def __str__(self):
        return self.original_name or self.file.name
