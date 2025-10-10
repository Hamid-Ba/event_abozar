"""
Content Admin Package
Imports all admin configurations
"""
from .base import BaseContentAdmin
from .news import NewsAdmin
from .education import EducationAdmin
from .event import EventAdmin

__all__ = ["BaseContentAdmin", "NewsAdmin", "EducationAdmin", "EventAdmin"]
