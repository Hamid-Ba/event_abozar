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
    FestivalListView,
    FeaturedFestivalListView,
    FestivalDetailView,
    FestivalRegisterView,
    FestivalMyWorksView,
    MyFestivalsView,
    UploadRulesView,
    WorkFilesView,
    WorkFileDetailView,
    JudgeWorkListView,
    JudgeWorkDetailView,
    JudgeReviewCreateView,
    JudgeMyReviewsView,
    AdminJudgedWorksView,
    NotificationListView,
    NotificationUnreadCountView,
    NotificationReadView,
)

app_name = "festival"

urlpatterns = [
    # Notifications (اعلان‌ها)
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path(
        "notifications/unread-count/",
        NotificationUnreadCountView.as_view(),
        name="notifications-unread-count",
    ),
    path("notifications/read-all/", NotificationReadView.as_view(), name="notifications-read-all"),
    path("notifications/<int:pk>/read/", NotificationReadView.as_view(), name="notification-read"),
    # Judging (داوری)
    path("judge/works/", JudgeWorkListView.as_view(), name="judge-works"),
    path("judge/works/<int:pk>/", JudgeWorkDetailView.as_view(), name="judge-work-detail"),
    path(
        "judge/works/<int:pk>/review/",
        JudgeReviewCreateView.as_view(),
        name="judge-review-create",
    ),
    path("judge/my-reviews/", JudgeMyReviewsView.as_view(), name="judge-my-reviews"),
    path("admin/judged-works/", AdminJudgedWorksView.as_view(), name="admin-judged-works"),
    # Festivals (چند جشنواره هم‌زمان)
    path("festivals/", FestivalListView.as_view(), name="festival-list"),
    path(
        "festivals/featured/",
        FeaturedFestivalListView.as_view(),
        name="festival-featured",
    ),
    path("festivals/<int:id>/", FestivalDetailView.as_view(), name="festival-detail"),
    path(
        "festivals/<int:id>/register/",
        FestivalRegisterView.as_view(),
        name="festival-register",
    ),
    path(
        "festivals/<int:id>/my-works/",
        FestivalMyWorksView.as_view(),
        name="festival-my-works",
    ),
    path("my-festivals/", MyFestivalsView.as_view(), name="my-festivals"),
    path("upload-rules/", UploadRulesView.as_view(), name="upload-rules"),
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
    path("works/<int:pk>/files/", WorkFilesView.as_view(), name="work-files"),
    path(
        "works/<int:pk>/files/<int:file_id>/",
        WorkFileDetailView.as_view(),
        name="work-file-detail",
    ),
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
