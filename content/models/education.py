"""
Education Model
Model for managing educational content
"""
from .base import BaseContentModel


class Education(BaseContentModel):
    """
    Education model for managing educational content
    """

    class Meta:
        verbose_name = "آموزش"
        verbose_name_plural = "آموزش‌ها"
        ordering = ["-publish_date"]
