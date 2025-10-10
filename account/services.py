from random import randint
from django.core.cache import cache

from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from monitoring.models.observability import CodeLog
from notifications import KavenegarSMS


@transaction.atomic
def generate_otp(phone: str):
    """Register User Service"""
    otp = randint(100000, 999999)

    cache.set(f"otp_{phone}", otp, timeout=60)  # store for 1 minutes

    if not settings.DEBUG:
        sms = KavenegarSMS()
        sms.register(
            receptor=phone,
            code=otp,
        )
        sms.send()

    return otp


def verify_otp(phone, otp_input):
    key = f"otp_{phone}"
    stored_otp = cache.get(key)

    if stored_otp and str(stored_otp) == str(otp_input):
        cache.delete(key)
        return True
    return False


@transaction.atomic
def get_or_create_user(phone, otp):
    """Get Or Create User Service"""

    user, created = get_user_model().objects.get_or_create(phone=phone)
    # user.set_password(str(otp))

    if settings.DEBUG:
        user.fullName = str(otp)

    user.save()

    return user


def generate_jwt(phone: str):
    """Generate JWT"""

    user = get_user_model().objects.filter(phone=phone).first()

    if user:
        refresh = RefreshToken.for_user(user)
        return refresh

    return None
