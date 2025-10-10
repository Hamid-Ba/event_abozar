"""
Festival Registration Services
"""
from django.db import transaction
from django.contrib.auth import get_user_model
from festival.models import FestivalRegistration

User = get_user_model()


@transaction.atomic
def create_festival_registration(phone_number, registration_data):
    """
    Create or get user by phone number and create festival registration
    """
    # Get or create user by phone number
    user, created = User.objects.get_or_create(phone=phone_number)

    # If user is new, we can set some basic info from registration data
    if created or not user.fullName:
        user.fullName = registration_data.get("full_name", "")
        user.save()

    # Create festival registration
    registration = FestivalRegistration.objects.create(user=user, **registration_data)

    return registration, created
