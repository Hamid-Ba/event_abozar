"""
Event Admin Configuration
"""
from django.contrib import admin
from .base import BaseContentAdmin
from content.models import Event


@admin.register(Event)
class EventAdmin(BaseContentAdmin):
    """
    Admin configuration for Event model
    """

    pass
