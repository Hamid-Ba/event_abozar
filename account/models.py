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
    """Custom User Model"""

    phone = models.CharField(max_length=11, unique=True, validators=[phone_validator])
    email = models.EmailField(null=True, blank=True)
    fullName = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    image = models.ImageField(null=True, blank=True, upload_to=image_file_path)

    USERNAME_FIELD = "phone"

    objects = UserManager()

    def __str__(self):
        if self.fullName:
            return self.fullName
        return self.phone
