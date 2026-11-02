"""
Judging Models
داوری: هر داور به هر اثر یک‌بار امتیاز می‌دهد؛ امتیاز نهایی اثر مجموع امتیاز همهٔ داوران است.
"""
from django.conf import settings
from django.db import models

from .festival import Festival
from .work import Work


class JudgeProfile(models.Model):
    """
    داور. مدیر یک کاربر می‌سازد (نام کاربری = شماره تلفن + رمز)، این پروفایل را برایش می‌سازد
    و جشنواره‌هایی که اجازهٔ داوری آن‌ها را دارد انتخاب می‌کند.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="judge_profile",
        verbose_name="کاربر",
    )
    festivals = models.ManyToManyField(
        Festival,
        blank=True,
        related_name="judges",
        verbose_name="جشنواره‌های قابل داوری",
        help_text="داور فقط آثار این جشنواره‌ها را می‌بیند",
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "داور"
        verbose_name_plural = "داوران"

    def __str__(self):
        return str(self.user)


class Review(models.Model):
    """امتیاز یک داور به یک اثر"""

    work = models.ForeignKey(
        Work, on_delete=models.CASCADE, related_name="reviews", verbose_name="اثر"
    )
    judge = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="festival_reviews",
        verbose_name="داور",
    )
    score = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="امتیاز"
    )
    note = models.TextField(blank=True, verbose_name="یادداشت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "امتیاز داور"
        verbose_name_plural = "امتیازهای داوران"
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["work", "judge"], name="unique_review_per_work_judge"
            )
        ]

    def __str__(self):
        return f"{self.judge} → {self.work_id}: {self.score}"
