from django.apps import AppConfig


class FestivalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "festival"

    def ready(self):
        from . import signals  # noqa: F401
