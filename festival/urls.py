"""
Festival Registration URLs
"""
from django.urls import path
from festival.views import (
    FestivalRegistrationCreateView,
    FestivalRegistrationListView,
    FestivalRegistrationDetailView,
    FestivalRegistrationSearchView,
    ProvinceListView,
    CityListView,
    WorkListCreateView,
    WorkDetailView,
    UserFestivalRegistrationsView,
    MyFestivalRegistrationListView,
    MyFestivalRegistrationDetailView,
    StatisticsView,
    MyStatisticsView,
    WorkByFestivalView,
    FestivalFormatListView,
    FestivalTopicListView,
    FestivalSpecialSectionListView,
)

app_name = "festival"

urlpatterns = [
    # Festival Registration endpoints
    path(
        "registration/",
        FestivalRegistrationCreateView.as_view(),
        name="registration-create",
    ),
    path(
        "registrations/",
        FestivalRegistrationListView.as_view(),
        name="registration-list",
    ),
    path(
        "registrations/<int:id>/",
        FestivalRegistrationDetailView.as_view(),
        name="registration-detail",
    ),
    path(
        "registrations/search/",
        FestivalRegistrationSearchView.as_view(),
        name="registration-search",
    ),
    # Province and City endpoints
    path("provinces/", ProvinceListView.as_view(), name="province-list"),
    path("cities/", CityListView.as_view(), name="city-list"),
    # Category endpoints
    path("formats/", FestivalFormatListView.as_view(), name="format-list"),
    path("topics/", FestivalTopicListView.as_view(), name="topic-list"),
    path(
        "special-sections/",
        FestivalSpecialSectionListView.as_view(),
        name="special-section-list",
    ),
    # Work endpoints
    path("works/", WorkListCreateView.as_view(), name="work-list"),
    path("works/<int:pk>/", WorkDetailView.as_view(), name="work-detail"),
    path(
        "works/by-festival/<int:festival_id>/",
        WorkByFestivalView.as_view(),
        name="work-list-by-festival",
    ),
    # User's festival registrations (for work creation)
    path(
        "my-registrations/",
        UserFestivalRegistrationsView.as_view(),
        name="user-registrations",
    ),
    # Authenticated user's festival registrations (list and detail)
    path(
        "my-registrations-list/",
        MyFestivalRegistrationListView.as_view(),
        name="my-registrations-list",
    ),
    path(
        "my-registrations-detail/<int:id>/",
        MyFestivalRegistrationDetailView.as_view(),
        name="my-registration-detail",
    ),
    # Statistics endpoints
    path(
        "statistics/",
        StatisticsView.as_view(),
        name="statistics",
    ),
    path(
        "my-statistics/",
        MyStatisticsView.as_view(),
        name="my-statistics",
    ),
]
