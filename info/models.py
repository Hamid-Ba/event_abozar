"""
Info App Models
Models for contact us, about us and related information
"""
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class ContactUs(models.Model):
    """
    Model for storing contact us messages
    مدل ذخیره پیام‌های تماس با ما
    """

    # Iranian mobile number validator
    phone_validator = RegexValidator(
        regex=r"^09\d{9}$", message="شماره تلفن باید به فرم 09XXXXXXXXX باشد"
    )

    full_name = models.CharField(
        max_length=100, verbose_name="نام کامل", help_text="نام و نام خانوادگی کامل"
    )

    phone = models.CharField(
        max_length=11,
        validators=[phone_validator],
        verbose_name="شماره تلفن",
        help_text="شماره موبایل (مثال: 09123456789)",
    )

    email = models.EmailField(verbose_name="ایمیل", help_text="آدرس ایمیل معتبر")

    message = models.TextField(verbose_name="پیام", help_text="متن پیام شما")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        verbose_name = "پیام تماس"
        verbose_name_plural = "پیام‌های تماس"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.phone}"

    def clean(self):
        """Custom validation"""
        super().clean()

        # Additional phone validation
        if self.phone and not self.phone.startswith("09"):
            raise ValidationError({"phone": "شماره تلفن باید با 09 شروع شود"})

        if self.phone and len(self.phone) != 11:
            raise ValidationError({"phone": "شماره تلفن باید 11 رقم باشد"})
