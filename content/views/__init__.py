"""
Content Views Package
Exports all view classes
"""
from .base import BaseContentListView, BaseContentDetailView
from .news import NewsListView, NewsDetailView
from .education import EducationListView, EducationDetailView
from .event import EventListView, EventDetailView

__all__ = [
    "BaseContentListView",
    "BaseContentDetailView",
    "NewsListView",
    "NewsDetailView",
    "EducationListView",
    "EducationDetailView",
    "EventListView",
    "EventDetailView",
]
