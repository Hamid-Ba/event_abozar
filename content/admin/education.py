"""
Education Admin Configuration
"""
from django.contrib import admin
from .base import BaseContentAdmin
from content.models import Education


@admin.register(Education)
class EducationAdmin(BaseContentAdmin):
    """
    Admin configuration for Education model
    """

    pass
