"""
Festival Admin
مدیریت جشنواره‌ها: تعریف جشنواره، بازهٔ ثبت‌نام، نمایش در صفحه اول و ترتیب
"""
import jdatetime
from django.contrib import admin
from django.db.models import Count
from django.utils import timezone
from django.utils.html import format_html

from festival.models import Festival

STATUS_STYLE = {
    Festival.STATUS_OPEN: ("#28a745", "باز"),
    Festival.STATUS_UPCOMING: ("#007bff", "به‌زودی"),
    Festival.STATUS_CLOSED: ("#6c757d", "بسته / آرشیو"),
}


def _jalali(value):
    if not value:
        return "-"
    local = timezone.localtime(value) if timezone.is_aware(value) else value
    return jdatetime.datetime.fromgregorian(datetime=local).strftime("%Y/%m/%d %H:%M")


@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "display_status",
        "display_start",
        "display_end",
        "is_active",
        "is_featured",
        "display_order",
        "registrations_count",
    )
    list_editable = ("is_active", "is_featured", "display_order")
    list_filter = ("is_active", "is_featured")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("formats", "topics", "special_sections")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("display_order", "-registration_start")

    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("title", "slug", "description", "banner")}),
        (
            "بازهٔ ثبت‌نام",
            {
                "fields": ("registration_start", "registration_end"),
                "description": "پس از پایان این بازه، جشنواره به آرشیو می‌رود و ثبت‌نام/ارسال اثر بسته می‌شود.",
            },
        ),
        (
            "نمایش",
            {
                "fields": ("is_active", "is_featured", "display_order"),
                "description": "«نمایش در صفحه اول» را برای جشنواره‌هایی که می‌خواهید در صفحه اول باشند تیک بزنید؛ مستقل از تاریخ.",
            },
        ),
        (
            "قالب‌ها، محورها و بخش‌های ویژه",
            {
                "fields": ("formats", "topics", "special_sections"),
                "description": "اگر برای هر مورد چیزی انتخاب نکنید، همهٔ موارد فعال در این جشنواره مجاز است.",
            },
        ),
        (
            "داوری",
            {
                "fields": ("required_judges", "max_score"),
                "description": "هر اثر پس از امتیاز دادن «تعداد داور لازم» نفر به‌طور خودکار «داوری‌شده» می‌شود. امتیاز نهایی = مجموع امتیاز داوران.",
            },
        ),
        ("اطلاعات سیستمی", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_registrations=Count("registrations"))

    @admin.display(description="وضعیت")
    def display_status(self, obj):
        color, label = STATUS_STYLE[obj.status]
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color,
            label,
        )

    @admin.display(description="شروع ثبت‌نام", ordering="registration_start")
    def display_start(self, obj):
        return _jalali(obj.registration_start)

    @admin.display(description="پایان ثبت‌نام", ordering="registration_end")
    def display_end(self, obj):
        return _jalali(obj.registration_end)

    @admin.display(description="تعداد ثبت‌نام", ordering="_registrations")
    def registrations_count(self, obj):
        return obj._registrations
