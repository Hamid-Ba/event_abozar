from django.contrib import admin

from province.models import Province, City

# Register your models here.


class ProvinceAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    list_display_links = ["id", "name"]
    search_fields = ["name"]


class CityAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "province"]
    list_display_links = ["id", "name"]
    list_filter = ["province"]
    search_fields = ["name", "province__name"]


admin.site.register(City, CityAdmin)
admin.site.register(Province, ProvinceAdmin)
