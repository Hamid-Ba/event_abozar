from django.core.cache import cache
from django.utils.timezone import timedelta


def set_cache(*, key: str, value, lock_minute: int):
    # Lock the API for the specified number of minutes
    lock_duration = timedelta(minutes=lock_minute)

    # Set the ads in cache
    cache.set(key, value, timeout=lock_duration.total_seconds())
