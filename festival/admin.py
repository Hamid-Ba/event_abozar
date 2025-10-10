"""
Festival Admin Configuration
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from festival.models import FestivalRegistration
from province.models import City


@admin.register(FestivalRegistration)
class FestivalRegistrationAdmin(admin.ModelAdmin):
    """Festival Registration Admin - Persian Interface"""

    list_display = [
        "full_name",
        "media_name",
        "festival_format",
        "festival_topic",
        "province",
        "city",
        "gender",
        "phone_number",
        "created_at",
    ]

    list_filter = [
        "festival_format",
        "festival_topic",
        "province",
        "city",
        "gender",
        "special_section",
        "created_at",
    ]

    search_fields = [
        "full_name",
        "father_name",
        "national_id",
        "phone_number",
        "media_name",
    ]

    readonly_fields = ["created_at", "updated_at"]

    # Persian list display headers
    list_display_links = ["full_name", "media_name"]

    fieldsets = (
        (
            "اطلاعات شخصی",
            {
                "fields": (
                    "full_name",
                    "father_name",
                    "national_id",
                    "gender",
                    "education",
                )
            },
        ),
        (
            "اطلاعات تماس",
            {"fields": ("phone_number", "virtual_number", "province", "city")},
        ),
        ("اطلاعات رسانه", {"fields": ("media_name",)}),
        (
            "تنظیمات جشنواره",
            {"fields": ("festival_format", "festival_topic", "special_section")},
        ),
        ("سایر اطلاعات", {"fields": ("user", "created_at", "updated_at")}),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:  # If editing an existing object
            readonly_fields.extend(["national_id", "phone_number", "user"])
        return readonly_fields

    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    class Media:
        js = ("admin/js/festival_admin.js",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "ajax/load-cities/",
                self.admin_site.admin_view(self.load_cities),
                name="festival_load_cities",
            ),
        ]
        return custom_urls + urls

    def load_cities(self, request):
        """AJAX endpoint to load cities based on province"""
        province_id = request.GET.get("province_id")
        cities = City.objects.filter(province_id=province_id).order_by("name")
        return JsonResponse(list(cities.values("id", "name")), safe=False)
