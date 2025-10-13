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
    WorkByFestivalView,
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
    "WorkByFestivalView",
    "MyFestivalRegistrationListView",
    "MyFestivalRegistrationDetailView",
    "StatisticsView",
    "MyStatisticsView",
]
