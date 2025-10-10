"""
Account Module Models
"""
import os
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

from account.vaidators import phone_validator


def image_file_path(instance, filename):
    """Generate file path for  image"""
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid4()}.{ext}"

    return os.path.join("uploads", "images", filename)


class UserManager(BaseUserManager):
    """User Manager"""

    def create_user(self, phone, password=None, **extra_fields):
        """Custome Create Normal User"""
        if not phone:
            raise ValueError
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """Create Super User"""
        if not phone:
            raise ValueError
        user = self.model(phone=phone, is_staff=True, is_superuser=True, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def get_admins(self):
        """Get Admin"""
        return self.filter(is_staff=True, is_superuser=True).all()


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User Model - Persian Interface"""

    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[phone_validator],
        verbose_name="شماره تلفن",
        help_text="شماره تلفن همراه کاربر",
    )
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name="ایمیل",
        help_text="آدرس ایمیل کاربر (اختیاری)",
    )
    fullName = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="نام کامل",
        help_text="نام و نام خانوادگی کاربر",
    )
    is_active = models.BooleanField(
        default=True, verbose_name="فعال", help_text="آیا کاربر فعال است؟"
    )
    is_staff = models.BooleanField(
        default=False, verbose_name="کارمند", help_text="آیا کاربر دسترسی ادمین دارد؟"
    )

    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=image_file_path,
        verbose_name="تصویر پروفایل",
        help_text="تصویر پروفایل کاربر",
    )

    USERNAME_FIELD = "phone"

    objects = UserManager()

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
        ordering = ["-id"]

    def __str__(self):
        if self.fullName:
            return self.fullName
        return self.phone
