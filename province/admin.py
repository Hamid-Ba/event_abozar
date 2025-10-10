from django.contrib import admin

from province.models import Province, City

# Register your models here.


class ProvinceAdmin(admin.ModelAdmin):
    """Persian Province Admin Interface"""

    list_display = ["id", "name"]
    list_display_links = ["id", "name"]
    search_fields = ["name"]

    fieldsets = (("اطلاعات استان", {"fields": ("name",)}),)

    def get_form(self, request, obj=None, **kwargs):
        """Customize form with Persian help texts"""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["name"].help_text = "نام استان را وارد کنید"
        return form


class CityAdmin(admin.ModelAdmin):
    """Persian City Admin Interface"""

    list_display = ["id", "name", "province"]
    list_display_links = ["id", "name"]
    list_filter = ["province"]
    search_fields = ["name", "province__name"]

    fieldsets = (("اطلاعات شهر", {"fields": ("name", "province")}),)

    def get_form(self, request, obj=None, **kwargs):
        """Customize form with Persian help texts"""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["name"].help_text = "نام شهر را وارد کنید"
        form.base_fields["province"].help_text = "استان مربوط به این شهر را انتخاب کنید"
        return form


admin.site.register(City, CityAdmin)
admin.site.register(Province, ProvinceAdmin)
