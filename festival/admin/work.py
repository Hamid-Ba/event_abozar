"""
Work Admin Configuration
تنظیمات مدیریت آثار جشنواره
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Count
from django.contrib.admin import SimpleListFilter

from festival.models import Work


class WorkRegistrationFilter(SimpleListFilter):
    """فیلتر بر اساس ثبت نام جشنواره"""

    title = "ثبت نام جشنواره"
    parameter_name = "festival_registration"

    def lookups(self, request, model_admin):
        registrations = (
            Work.objects.select_related("festival_registration")
            .values_list(
                "festival_registration__id", "festival_registration__full_name"
            )
            .distinct()[:50]
        )  # Limit for performance
        return registrations

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(festival_registration__id=self.value())
        return queryset


class MediaNameFilter(SimpleListFilter):
    """فیلتر بر اساس نام رسانه"""

    title = "نام رسانه"
    parameter_name = "media_name"

    def lookups(self, request, model_admin):
        media_names = (
            Work.objects.select_related("festival_registration")
            .values_list(
                "festival_registration__media_name", "festival_registration__media_name"
            )
            .distinct()[:20]
        )  # Limit for performance
        return media_names

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(festival_registration__media_name=self.value())
        return queryset


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    """مدیریت آثار جشنواره"""

    list_display = [
        "display_title",
        "display_registration_name",
        "display_media_name",
        "display_festival_format",
        "display_has_file",
        "display_created_date",
        "display_status",
    ]

    list_filter = [
        WorkRegistrationFilter,
        MediaNameFilter,
        "festival_registration__festival_format",
        "festival_registration__festival_topic",
        "created_at",
    ]

    search_fields = [
        "title",
        "description",
        "festival_registration__full_name",
        "festival_registration__media_name",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "display_file_info",
    ]

    fieldsets = [
        (
            "اطلاعات اثر",
            {
                "fields": [
                    "festival_registration",
                    "title",
                    "description",
                    "file",
                    "display_file_info",
                ],
                "classes": ["wide"],
            },
        ),
        (
            "اطلاعات سیستمی",
            {
                "fields": [
                    "created_at",
                    "updated_at",
                ],
                "classes": ["collapse", "wide"],
            },
        ),
    ]

    def get_queryset(self, request):
        """بهینه‌سازی کوئری‌ها"""
        return (
            super()
            .get_queryset(request)
            .select_related(
                "festival_registration",
                "festival_registration__province",
                "festival_registration__city",
            )
        )

    def display_title(self, obj):
        """نمایش عنوان اثر"""
        if len(obj.title) > 30:
            short_title = obj.title[:30] + "..."
            return format_html(
                '<span title="{}" class="work-title">{}</span>', obj.title, short_title
            )
        return format_html('<span class="work-title">{}</span>', obj.title)

    display_title.short_description = "عنوان اثر"
    display_title.admin_order_field = "title"

    def display_registration_name(self, obj):
        """نمایش نام ثبت نام کننده"""
        return format_html(
            '<span class="registration-name" style="color: #0066cc; font-weight: bold;">{}</span>',
            obj.festival_registration.full_name,
        )

    display_registration_name.short_description = "نام ثبت نام کننده"
    display_registration_name.admin_order_field = "festival_registration__full_name"

    def display_media_name(self, obj):
        """نمایش نام رسانه"""
        return format_html(
            '<span class="media-name" style="color: #ff6600; font-weight: bold;">{}</span>',
            obj.festival_registration.media_name,
        )

    display_media_name.short_description = "نام رسانه"
    display_media_name.admin_order_field = "festival_registration__media_name"

    def display_festival_format(self, obj):
        """نمایش قالب جشنواره"""
        if not obj.festival_registration.festival_format:
            return "-"

        format_code = obj.festival_registration.festival_format.code
        format_name = obj.festival_registration.festival_format.name

        # Color coding for different formats
        color_map = {
            "news_report": "#28a745",  # Green
            "interview": "#007bff",  # Blue
            "editorial": "#6f42c1",  # Purple
            "headline": "#fd7e14",  # Orange
            "infographic": "#20c997",  # Teal
            "motion_graphic": "#e83e8c",  # Pink
            "photo": "#ffc107",  # Yellow
            "video_clip": "#dc3545",  # Red
            "documentary": "#6c757d",  # Gray
            "podcast": "#17a2b8",  # Cyan
        }

        color = color_map.get(format_code, "#6c757d")

        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            format_name,
        )

    display_festival_format.short_description = "قالب جشنواره"
    display_festival_format.admin_order_field = "festival_registration__festival_format"

    def display_has_file(self, obj):
        """نمایش وضعیت فایل"""
        if obj.file:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ موجود</span>'
            )
        return format_html(
            '<span style="color: #dc3545; font-weight: bold;">✗ خطا</span>'
        )

    display_has_file.short_description = "فایل"
    display_has_file.admin_order_field = "file"

    def display_created_date(self, obj):
        """نمایش تاریخ ایجاد"""
        try:
            import jdatetime

            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
            return format_html(
                '<span dir="ltr" style="font-family: monospace;">{}</span>',
                jalali_date.strftime("%Y/%m/%d - %H:%M"),
            )
        except ImportError:
            # Fallback to regular datetime if jdatetime is not available
            return format_html(
                '<span dir="ltr" style="font-family: monospace;">{}</span>',
                obj.created_at.strftime("%Y/%m/%d - %H:%M"),
            )

    display_created_date.short_description = "تاریخ ایجاد"
    display_created_date.admin_order_field = "created_at"

    def display_status(self, obj):
        """نمایش وضعیت کلی اثر"""
        has_file = bool(obj.file)
        has_description = bool(obj.description and len(obj.description.strip()) > 1)

        if has_file and has_description:
            status_text = "کامل"
            color = "#28a745"  # Green
        elif has_file:
            status_text = "نیمه کامل"
            color = "#ffc107"  # Yellow
        else:
            status_text = "ناقص"
            color = "#dc3545"  # Red

        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            status_text,
        )

    display_status.short_description = "وضعیت"

    def display_file_info(self, obj):
        """نمایش اطلاعات فایل"""
        if obj.file:
            try:
                file_size = obj.file.size
                if file_size < 1024:
                    size_str = f"{file_size} بایت"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.1f} کیلوبایت"
                else:
                    size_str = f"{file_size / (1024 * 1024):.1f} مگابایت"

                # Extract unique filename and show file path structure
                file_path = obj.file.name
                unique_filename = (
                    file_path.split("/")[-1] if "/" in file_path else file_path
                )

                return format_html(
                    '<div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px;">'
                    "<strong>نام منحصر به فرد:</strong> <code>{}</code><br>"
                    '<strong>مسیر فایل:</strong> <small style="color: #6c757d;">{}</small><br>'
                    "<strong>حجم:</strong> {}<br>"
                    '<a href="{}" target="_blank" style="color: #007bff;">مشاهده فایل</a>'
                    "</div>",
                    unique_filename,
                    file_path,
                    size_str,
                    obj.file.url,
                )
            except Exception as e:
                return format_html(
                    '<div style="color: #dc3545;">خطا در دریافت اطلاعات فایل: {}</div>',
                    str(e),
                )
        return format_html('<div style="color: #6c757d;">فایلی آپلود نشده است</div>')

    display_file_info.short_description = "اطلاعات فایل"

    class Media:
        css = {"all": ["admin/css/work_admin.css"]}
        js = ["admin/js/work_admin.js"]

    def changelist_view(self, request, extra_context=None):
        """سفارشی‌سازی نمای لیست"""
        extra_context = extra_context or {}

        # آمار کلی
        total_works = Work.objects.count()
        works_with_files = Work.objects.exclude(file="").count()
        recent_works = Work.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()

        extra_context.update(
            {
                "total_works": total_works,
                "works_with_files": works_with_files,
                "recent_works": recent_works,
            }
        )

        return super().changelist_view(request, extra_context)
