"""
Province Module Models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Province(models.Model):
    """Province Model"""

    name = models.CharField(max_length=50, blank=False, null=False, verbose_name="نام")
    slug = models.SlugField(
        max_length=125, blank=False, null=False, verbose_name="اسلاگ"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("استان")
        verbose_name_plural = _("استان ها")

    # def get_absolute_url(self):
    #     return reverse("cafe:cafes_by_province", kwargs={"province_slug": self.slug})


class City(models.Model):
    """City Model"""

    name = models.CharField(max_length=85, blank=False, null=False, verbose_name="نام")
    slug = models.SlugField(
        max_length=225, blank=False, null=False, verbose_name="اسلاگ"
    )
    province = models.ForeignKey(
        Province,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name="استان",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("شهر")
        verbose_name_plural = _("شهر ها")
