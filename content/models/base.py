"""
Base Content Model
Abstract base model for content with common fields
"""
from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField


class BaseContentModel(models.Model):
    """
    Abstract base model for content with common fields
    """

    title = models.CharField(
        max_length=200, verbose_name="عنوان", help_text="عنوان محتوا"
    )
    description = RichTextField(verbose_name="توضیحات", help_text="توضیحات کامل محتوا")
    image = models.ImageField(
        upload_to="content/images/",
        blank=True,
        null=True,
        verbose_name="تصویر",
        help_text="تصویر مرتبط با محتوا",
    )
    publish_date = models.DateField(
        default=timezone.now,
        verbose_name="تاریخ انتشار",
        help_text="تاریخ انتشار محتوا",
    )
    tags = TaggableManager(
        verbose_name="برچسب‌ها", help_text="برچسب‌های مرتبط با محتوا", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        abstract = True
        ordering = ["-publish_date"]

    def __str__(self):
        return self.title
