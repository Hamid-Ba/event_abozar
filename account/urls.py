"""
Account Module Mapper
"""
from django.urls import (
    path,
)

from account import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

# router = DefaultRouter()
# router.register("auth",views.AuthenticationViewSet , basename='auth')

app_name = "account"

urlpatterns = [
    # Authentication endpoints
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("me/", views.UserView.as_view(), name="me"),
    # JWT token management
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("verify/", TokenVerifyView.as_view(), name="verify"),
]
