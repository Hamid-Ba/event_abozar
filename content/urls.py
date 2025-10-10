"""
Content URLs
URL patterns for News, Education, and Event endpoints
"""
from django.urls import path
from .views import (
    NewsListView,
    NewsDetailView,
    EducationListView,
    EducationDetailView,
    EventListView,
    EventDetailView,
)

app_name = "content"

urlpatterns = [
    # News endpoints
    path("news/", NewsListView.as_view(), name="news-list"),
    path("news/<int:pk>/", NewsDetailView.as_view(), name="news-detail"),
    # Education endpoints
    path("education/", EducationListView.as_view(), name="education-list"),
    path("education/<int:pk>/", EducationDetailView.as_view(), name="education-detail"),
    # Event endpoints
    path("events/", EventListView.as_view(), name="event-list"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
]
