"""
Festival Registration Admin Configuration
جشنواره رسانه ای ابوذر - تنظیمات مدیریت ثبت نام
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Count
from django.contrib.admin import SimpleListFilter

from festival.models import FestivalRegistration
from province.models import City


class FestivalFormatFilter(SimpleListFilter):
    """فیلتر قالب جشنواره"""

    title = "قالب جشنواره"
    parameter_name = "festival_format"

    def lookups(self, request, model_admin):
        return FestivalRegistration.FORMAT_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(festival_format=self.value())
        return queryset


class FestivalTopicFilter(SimpleListFilter):
    """فیلتر محور جشنواره"""

    title = "محور جشنواره"
    parameter_name = "festival_topic"

    def lookups(self, request, model_admin):
        return FestivalRegistration.TOPIC_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(festival_topic=self.value())
        return queryset


class GenderFilter(SimpleListFilter):
    """فیلتر جنسیت"""

    title = "جنسیت"
    parameter_name = "gender"

    def lookups(self, request, model_admin):
        return FestivalRegistration.GENDER_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(gender=self.value())
        return queryset


@admin.register(FestivalRegistration)
class FestivalRegistrationAdmin(admin.ModelAdmin):
    """
    مدیریت ثبت نام جشنواره رسانه ای ابوذر
    Festival Registration Admin - Persian Interface
    """

    list_display = [
        "display_full_name",
        "display_media_name",
        "display_festival_format",
        "display_festival_topic",
        "display_province_city",
        "display_gender",
        "display_phone",
        "display_created_date",
        "display_status",
    ]

    list_filter = [
        FestivalFormatFilter,
        FestivalTopicFilter,
        GenderFilter,
        "province",
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

    readonly_fields = [
        "created_at",
        "updated_at",
        "display_registration_summary",
    ]

    list_display_links = ["display_full_name", "display_media_name"]

    list_per_page = 25
    list_max_show_all = 100

    fieldsets = (
        (
            "📋 اطلاعات شخصی",
            {
                "fields": (
                    "full_name",
                    "father_name",
                    "national_id",
                    "gender",
                    "education",
                ),
                "description": "اطلاعات هویتی و شخصی متقاضی",
            },
        ),
        (
            "📞 اطلاعات تماس و آدرس",
            {
                "fields": ("phone_number", "virtual_number", "province", "city"),
                "description": "اطلاعات تماس و محل سکونت",
            },
        ),
        (
            "📺 اطلاعات رسانه",
            {"fields": ("media_name",), "description": "نام رسانه یا نشریه"},
        ),
        (
            "🏆 تنظیمات جشنواره",
            {
                "fields": ("festival_format", "festival_topic", "special_section"),
                "description": "قالب، محور و بخش ویژه جشنواره",
            },
        ),
        (
            "👤 اطلاعات سیستم",
            {
                "fields": (
                    "user",
                    "display_registration_summary",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
                "description": "اطلاعات سیستمی و کاربر",
            },
        ),
    )

    # Persian column headers
    def display_full_name(self, obj):
        """نمایش نام کامل"""
        return format_html('<strong style="color: #0066cc;">{}</strong>', obj.full_name)

    display_full_name.short_description = "نام کامل"
    display_full_name.admin_order_field = "full_name"

    def display_media_name(self, obj):
        """نمایش نام رسانه"""
        return format_html(
            '<span style="color: #009900; font-weight: bold;">{}</span>',
            obj.media_name or "نامشخص",
        )

    display_media_name.short_description = "رسانه"
    display_media_name.admin_order_field = "media_name"

    def display_festival_format(self, obj):
        """نمایش قالب جشنواره"""
        format_colors = {
            "news_report": "#FF6B35",
            "interview": "#004E89",
            "editorial": "#7209B7",
            "headline": "#F72585",
            "infographic": "#4CC9F0",
            "motion_graphic": "#7209B7",
            "photo": "#F77F00",
            "video_clip": "#FCBF49",
            "documentary": "#003566",
            "podcast": "#6A994E",
        }
        color = format_colors.get(obj.festival_format, "#666666")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_festival_format_display(),
        )

    display_festival_format.short_description = "قالب"
    display_festival_format.admin_order_field = "festival_format"

    def display_festival_topic(self, obj):
        """نمایش محور جشنواره"""
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{}</span>',
            obj.get_festival_topic_display(),
        )

    display_festival_topic.short_description = "محور"
    display_festival_topic.admin_order_field = "festival_topic"

    def display_province_city(self, obj):
        """نمایش استان و شهر"""
        return f"{obj.province.name} - {obj.city.name if obj.city else 'نامشخص'}"

    display_province_city.short_description = "استان - شهر"
    display_province_city.admin_order_field = "province__name"

    def display_gender(self, obj):
        """نمایش جنسیت"""
        gender_icons = {"male": "👨", "female": "👩"}
        icon = gender_icons.get(obj.gender, "❓")
        return f"{icon} {obj.get_gender_display()}"

    display_gender.short_description = "جنسیت"
    display_gender.admin_order_field = "gender"

    def display_phone(self, obj):
        """نمایش شماره تلفن"""
        return format_html(
            '<span style="direction: ltr; font-family: monospace;">{}</span>',
            obj.phone_number,
        )

    display_phone.short_description = "تلفن"
    display_phone.admin_order_field = "phone_number"

    def display_created_date(self, obj):
        """نمایش تاریخ ثبت"""
        return obj.created_at.strftime("%Y/%m/%d %H:%M")

    display_created_date.short_description = "تاریخ ثبت"
    display_created_date.admin_order_field = "created_at"

    def display_status(self, obj):
        """نمایش وضعیت"""
        if obj.special_section:
            return format_html(
                '<span style="background-color: #ffc107; color: #212529; padding: 2px 6px; border-radius: 3px; font-size: 10px;">ویژه</span>'
            )
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">عادی</span>'
        )

    display_status.short_description = "وضعیت"

    def display_registration_summary(self, obj):
        """خلاصه ثبت نام"""
        if obj.pk:
            return format_html(
                """
                <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    <h4 style="color: #495057; margin: 0 0 10px 0;">📊 خلاصه ثبت نام</h4>
                    <p><strong>👤 نام:</strong> {}</p>
                    <p><strong>📱 تلفن:</strong> <span style="direction: ltr;">{}</span></p>
                    <p><strong>🎬 قالب:</strong> {}</p>
                    <p><strong>🎯 محور:</strong> {}</p>
                    <p><strong>📍 محل:</strong> {} - {}</p>
                    <p><strong>📅 تاریخ ثبت:</strong> {}</p>
                </div>
                """,
                obj.full_name,
                obj.phone_number,
                obj.get_festival_format_display(),
                obj.get_festival_topic_display(),
                obj.province.name,
                obj.city.name if obj.city else "نامشخص",
                obj.created_at.strftime("%Y/%m/%d %H:%M"),
            )
        return "اطلاعات پس از ذخیره نمایش داده می‌شود"

    display_registration_summary.short_description = "خلاصه اطلاعات"

    def get_readonly_fields(self, request, obj=None):
        """تنظیم فیلدهای فقط خواندنی"""
        readonly_fields = list(self.readonly_fields)
        if obj:  # If editing an existing object
            readonly_fields.extend(["national_id", "phone_number", "user"])
        return readonly_fields

    def get_queryset(self, request):
        """بهینه‌سازی کوئری با select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "province", "city")

    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    # Actions
    actions = ["export_to_excel", "mark_as_special"]

    def export_to_excel(self, request, queryset):
        """خروجی اکسل"""
        # TODO: Implement Excel export functionality
        self.message_user(
            request, f"{queryset.count()} رکورد انتخاب شد برای خروجی اکسل"
        )

    export_to_excel.short_description = "خروجی اکسل از موارد انتخابی"

    def mark_as_special(self, request, queryset):
        """علامت‌گذاری به عنوان بخش ویژه"""
        count = queryset.update(special_section=True)
        self.message_user(request, f"{count} مورد به بخش ویژه منتقل شد")

    mark_as_special.short_description = "انتقال به بخش ویژه"

    class Media:
        css = {"all": ("admin/css/festival_admin.css",)}
        js = ("admin/js/festival_admin.js",)

    def get_urls(self):
        """URL های سفارشی برای ادمین"""
        urls = super().get_urls()
        custom_urls = [
            path(
                "ajax/load-cities/",
                self.admin_site.admin_view(self.load_cities),
                name="festival_load_cities",
            ),
            path(
                "statistics/",
                self.admin_site.admin_view(self.statistics_view),
                name="festival_statistics",
            ),
        ]
        return custom_urls + urls

    def load_cities(self, request):
        """
        AJAX endpoint to load cities based on province
        بارگذاری شهرها بر اساس استان انتخابی
        """
        province_id = request.GET.get("province_id")
        cities = City.objects.filter(province_id=province_id).order_by("name")
        return JsonResponse(
            list(cities.values("id", "name")),
            safe=False,
            json_dumps_params={"ensure_ascii": False},
        )

    def statistics_view(self, request):
        """
        نمایش آمار جشنواره
        Festival statistics view
        """
        stats = {
            "total_registrations": FestivalRegistration.objects.count(),
            "by_format": dict(
                FestivalRegistration.objects.values_list("festival_format").annotate(
                    count=Count("festival_format")
                )
            ),
            "by_topic": dict(
                FestivalRegistration.objects.values_list("festival_topic").annotate(
                    count=Count("festival_topic")
                )
            ),
            "by_gender": dict(
                FestivalRegistration.objects.values_list("gender").annotate(
                    count=Count("gender")
                )
            ),
        }
        return JsonResponse(stats, json_dumps_params={"ensure_ascii": False})

    def changelist_view(self, request, extra_context=None):
        """
        سفارشی‌سازی نمای لیست
        Custom changelist view with statistics
        """
        extra_context = extra_context or {}

        # Add statistics to context
        extra_context["total_registrations"] = FestivalRegistration.objects.count()
        extra_context["today_registrations"] = (
            FestivalRegistration.objects.filter(
                created_at__date=timezone.now().date()
            ).count()
            if "timezone" in globals()
            else 0
        )

        return super().changelist_view(request, extra_context)
