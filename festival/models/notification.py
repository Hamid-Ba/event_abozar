"""
Notification
اعلان درون‌برنامه برای شرکت‌کننده/داور (تغییر وضعیت اثر، بازشدن نظرسنجی)
"""
from django.conf import settings
from django.db import models


class Notification(models.Model):
    KIND_WORK_STATUS = "work_status"
    KIND_FORM_OPENED = "form_opened"
    KIND_CHOICES = [
        (KIND_WORK_STATUS, "تغییر وضعیت اثر"),
        (KIND_FORM_OPENED, "بازشدن نظرسنجی"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="festival_notifications",
        verbose_name="کاربر",
    )
    kind = models.CharField(max_length=30, choices=KIND_CHOICES, verbose_name="نوع")
    title = models.CharField(max_length=255, verbose_name="عنوان")
    body = models.TextField(blank=True, verbose_name="متن")
    # شناسهٔ اثر یا فرم مربوط، برای لینک در فرانت
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="شناسه مرتبط")
    is_read = models.BooleanField(default=False, db_index=True, verbose_name="خوانده‌شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ")

    class Meta:
        verbose_name = "اعلان"
        verbose_name_plural = "اعلان‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_id}: {self.title}"
