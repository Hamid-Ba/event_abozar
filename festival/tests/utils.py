"""
Test helpers
"""
from datetime import timedelta

from django.utils import timezone

from festival.models import Festival

_counter = {"n": 0}


def make_festival(**overrides):
    """یک جشنواره باز (پیش‌فرض) می‌سازد؛ با overrides می‌شود بسته/آینده/ویژه‌اش کرد"""
    _counter["n"] += 1
    now = timezone.now()
    data = {
        "title": f"جشنواره تست {_counter['n']}",
        "slug": f"test-festival-{_counter['n']}",
        "registration_start": now - timedelta(days=1),
        "registration_end": now + timedelta(days=30),
        "is_active": True,
    }
    data.update(overrides)
    return Festival.objects.create(**data)
