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
]
