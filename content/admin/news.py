"""
News Admin Configuration
"""
from django.contrib import admin
from .base import BaseContentAdmin
from content.models import News


@admin.register(News)
class NewsAdmin(BaseContentAdmin):
    """
    Admin configuration for News model
    """

    pass
