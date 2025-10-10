from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProvinceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "province"
    verbose_name = _("استان")
