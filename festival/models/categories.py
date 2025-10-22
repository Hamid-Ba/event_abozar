"""
Festival Category Models
دسته‌بندی‌های جشنواره (قالب، محور، بخش ویژه)
"""
from django.db import models


class FestivalFormat(models.Model):
    """Festival Format Model - قالب‌های جشنواره"""

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد قالب",
        help_text="کد یکتای قالب (انگلیسی)",
    )
    name = models.CharField(
        max_length=200, verbose_name="نام قالب", help_text="نام فارسی قالب"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات",
        help_text="توضیحات تکمیلی درباره این قالب",
    )
    is_active = models.BooleanField(
        default=True, verbose_name="فعال", help_text="آیا این قالب فعال است؟"
    )
    display_order = models.IntegerField(
        default=0, verbose_name="ترتیب نمایش", help_text="ترتیب نمایش در لیست‌ها"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        verbose_name = "قالب جشنواره"
        verbose_name_plural = "قالب‌های جشنواره"
        ordering = ["name"]

    def __str__(self):
        return self.name


class FestivalTopic(models.Model):
    """Festival Topic Model - محورهای جشنواره"""

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد محور",
        help_text="کد یکتای محور (انگلیسی)",
    )
    name = models.CharField(
        max_length=200, verbose_name="نام محور", help_text="نام فارسی محور"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات",
        help_text="توضیحات تکمیلی درباره این محور",
    )
    is_active = models.BooleanField(
        default=True, verbose_name="فعال", help_text="آیا این محور فعال است؟"
    )
    display_order = models.IntegerField(
        default=0, verbose_name="ترتیب نمایش", help_text="ترتیب نمایش در لیست‌ها"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        verbose_name = "محور جشنواره"
        verbose_name_plural = "محورهای جشنواره"
        ordering = ["name"]

    def __str__(self):
        return self.name


class FestivalSpecialSection(models.Model):
    """Festival Special Section Model - بخش‌های ویژه جشنواره"""

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد بخش",
        help_text="کد یکتای بخش (انگلیسی)",
    )
    name = models.CharField(
        max_length=200, verbose_name="نام بخش", help_text="نام فارسی بخش ویژه"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات",
        help_text="توضیحات تکمیلی درباره این بخش",
    )
    is_active = models.BooleanField(
        default=True, verbose_name="فعال", help_text="آیا این بخش فعال است؟"
    )
    display_order = models.IntegerField(
        default=0, verbose_name="ترتیب نمایش", help_text="ترتیب نمایش در لیست‌ها"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        verbose_name = "بخش ویژه جشنواره"
        verbose_name_plural = "بخش‌های ویژه جشنواره"
        ordering = ["name"]

    def __str__(self):
        return self.name
