"""
News Model
Model for managing news content
"""
from .base import BaseContentModel


class News(BaseContentModel):
    """
    News model for managing news content
    """

    class Meta:
        verbose_name = "خبر"
        verbose_name_plural = "اخبار"
        ordering = ["-publish_date"]
