from django.urls import path

from formbuilder import views

app_name = "formbuilder"

urlpatterns = [
    path("", views.FormListView.as_view(), name="form-list"),
    path("<int:pk>/", views.FormDetailView.as_view(), name="form-detail"),
    path("<int:pk>/submit/", views.FormSubmitView.as_view(), name="form-submit"),
    path(
        "judging/works/<int:pk>/review/",
        views.JudgingFormReviewView.as_view(),
        name="judging-review",
    ),
    path(
        "admin/<int:pk>/submissions/",
        views.AdminSubmissionsView.as_view(),
        name="admin-submissions",
    ),
    path("admin/<int:pk>/summary/", views.AdminSummaryView.as_view(), name="admin-summary"),
    path("admin/<int:pk>/export/", views.AdminExportView.as_view(), name="admin-export"),
]
