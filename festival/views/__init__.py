from .festival_registration import (
    FestivalRegistrationCreateView,
    FestivalRegistrationListView,
    FestivalRegistrationDetailView,
    FestivalRegistrationSearchView,
    ProvinceListView,
    CityListView,
    MyFestivalRegistrationListView,
    MyFestivalRegistrationDetailView,
    StatisticsView,
    MyStatisticsView,
)

from .work import (
    WorkListCreateView,
    WorkDetailView,
    UserFestivalRegistrationsView,
)

__all__ = [
    "FestivalRegistrationCreateView",
    "FestivalRegistrationListView",
    "FestivalRegistrationDetailView",
    "FestivalRegistrationSearchView",
    "ProvinceListView",
    "CityListView",
    "WorkListCreateView",
    "WorkDetailView",
    "UserFestivalRegistrationsView",
    "MyFestivalRegistrationListView",
    "MyFestivalRegistrationDetailView",
    "StatisticsView",
    "MyStatisticsView",
]
