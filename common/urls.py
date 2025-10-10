from django.urls import path
from .views import CreateSuperUserView

urlpatterns = [
    path("create-superuser/", CreateSuperUserView.as_view(), name="create-superuser"),
]
