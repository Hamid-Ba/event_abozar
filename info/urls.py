"""
Info URLs
URL patterns for info app endpoints
"""
from django.urls import path
from .views import ContactUsCreateView

app_name = "info"

urlpatterns = [
    # Contact Us endpoints
    path("contact-us/", ContactUsCreateView.as_view(), name="contact-us-create"),
]
