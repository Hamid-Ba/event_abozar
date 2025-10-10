"""
Event Model
Model for managing event content
"""
from .base import BaseContentModel


class Event(BaseContentModel):
    """
    Event model for managing event content
    """

    class Meta:
        verbose_name = "رویداد"
        verbose_name_plural = "رویدادها"
        ordering = ["-publish_date"]
