"""
Festival Registration Models
"""
from django.db import models
from django.contrib.auth import get_user_model
from province.models import Province, City
from .categories import FestivalFormat, FestivalTopic, FestivalSpecialSection

User = get_user_model()


class FestivalRegistration(models.Model):
    """Festival Registration Model for یازدهمین جشنواره رسانه ای ابوذر"""

    # Gender choices
    GENDER_CHOICES = [
        ("male", "مرد"),
        ("female", "زن"),
    ]

    # User relationship
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="festival_registrations"
    )

    # Personal Information
    full_name = models.CharField(max_length=255, verbose_name="نام و نام خانوادگی")
    father_name = models.CharField(max_length=100, verbose_name="نام پدر")
    national_id = models.CharField(max_length=10, verbose_name="کد ملی")
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, verbose_name="جنسیت"
    )
    education = models.CharField(max_length=255, verbose_name="تحصیلات")

    # Contact Information
    phone_number = models.CharField(max_length=11, verbose_name="شماره تماس")
    virtual_number = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="شماره مجازی"
    )
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, verbose_name="استان"
    )
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="شهر")

    # Media Information
    media_name = models.CharField(max_length=255, verbose_name="نام رسانه")

    # Festival Categories - Foreign Key Relationships
    festival_format = models.ForeignKey(
        FestivalFormat,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="قالب جشنواره",
    )
    festival_topic = models.ForeignKey(
        FestivalTopic,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="محور جشنواره",
    )
    special_section = models.ForeignKey(
        FestivalSpecialSection,
        on_delete=models.CASCADE,
        related_name="registrations",
        blank=True,
        null=True,
        verbose_name="بخش ویژه",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ثبت نام جشنواره"
        verbose_name_plural = "ثبت نام های جشنواره"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.media_name}"
