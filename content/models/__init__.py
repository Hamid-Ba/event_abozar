"""
Content Models Package
Exports all content models
"""
from .base import BaseContentModel
from .news import News
from .education import Education
from .event import Event

__all__ = ["BaseContentModel", "News", "Education", "Event"]
