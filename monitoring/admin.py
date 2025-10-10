from django.contrib import admin
from django.utils.html import format_html

from .models import CodeLog


@admin.register(CodeLog)
class CodeLogAdmin(admin.ModelAdmin):
    """Enhanced Persian Monitoring Admin Interface"""

    list_display = (
        "level_badge",
        "log_type_badge",
        "module",
        "method",
        "user",
        "timestamp",
        "duration",
        "is_exception",
        "is_resolved",
    )

    list_filter = (
        "level",
        "log_type",
        "module",
        "timestamp",
        "is_resolved",
        "exception_type",
        "request_method",
    )

    search_fields = (
        "module",
        "method",
        "message",
        "exception_message",
        "request_path",
        "user__fullName",
        "user__phone",
        "tags",
    )

    ordering = ("-timestamp",)
    readonly_fields = (
        "timestamp",
        "cpu_usage",
        "memory_usage",
        "traceback_info",
        "severity_score",
    )
    list_display_links = ("level_badge", "module")
    list_per_page = 50

    # Enhanced fieldsets for better organization
    fieldsets = (
        (
            "🔍 اطلاعات اصلی لاگ",
            {
                "fields": (
                    ("level", "log_type"),
                    ("module", "method"),
                    "message",
                    "tags",
                    ("is_resolved", "resolution_note"),
                )
            },
        ),
        (
            "👤 اطلاعات کاربر و درخواست",
            {
                "fields": (
                    "user",
                    ("request_path", "request_method"),
                    ("ip_address", "user_agent"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "⚠️ اطلاعات استثنا و خطا",
            {
                "fields": (
                    ("exception_type", "exception_message"),
                    "traceback_info",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "📊 عملکرد و زمان‌بندی",
            {
                "fields": (
                    ("timestamp", "duration"),
                    ("cpu_usage", "memory_usage"),
                    "severity_score",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "🔧 اطلاعات تکمیلی",
            {
                "fields": ("context",),
                "classes": ("collapse",),
            },
        ),
    )

    # Custom admin methods for better display
    def level_badge(self, obj):
        """Display level with color coding"""
        colors = {
            "DEBUG": "gray",
            "INFO": "blue",
            "WARNING": "orange",
            "ERROR": "red",
            "CRITICAL": "darkred",
            "EXCEPTION": "purple",
            "SECURITY": "maroon",
            "PERFORMANCE": "green",
        }
        color = colors.get(obj.level, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_level_display(),
        )

    level_badge.short_description = "سطح"
    level_badge.admin_order_field = "level"

    def log_type_badge(self, obj):
        """Display log type with badge styling"""
        return format_html(
            '<span class="badge" style="background: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            obj.get_log_type_display(),
        )

    log_type_badge.short_description = "نوع"
    log_type_badge.admin_order_field = "log_type"

    def is_exception(self, obj):
        """Show if entry is an exception"""
        if obj.is_exception:
            return format_html('<span style="color: red;">✗ دارد</span>')
        return format_html('<span style="color: green;">✓ ندارد</span>')

    is_exception.short_description = "استثنا"
    is_exception.boolean = True

    # Custom actions
    actions = ["mark_as_resolved", "mark_as_unresolved", "export_critical_logs"]

    def mark_as_resolved(self, request, queryset):
        """Mark selected logs as resolved"""
        count = queryset.update(is_resolved=True)
        self.message_user(request, f"{count} لاگ به عنوان حل شده علامت‌گذاری شد.")

    mark_as_resolved.short_description = "علامت‌گذاری به عنوان حل شده"

    def mark_as_unresolved(self, request, queryset):
        """Mark selected logs as unresolved"""
        count = queryset.update(is_resolved=False)
        self.message_user(request, f"{count} لاگ به عنوان حل نشده علامت‌گذاری شد.")

    mark_as_unresolved.short_description = "علامت‌گذاری به عنوان حل نشده"

    def export_critical_logs(self, request, queryset):
        """Export critical logs for analysis"""
        critical_logs = queryset.filter(level__in=["CRITICAL", "ERROR", "EXCEPTION"])
        count = critical_logs.count()
        self.message_user(request, f"{count} لاگ بحرانی برای تجزیه و تحلیل انتخاب شد.")

    export_critical_logs.short_description = "استخراج لاگ‌های بحرانی"

    def get_form(self, request, obj=None, **kwargs):
        """Customize form with Persian help texts"""
        form = super().get_form(request, obj, **kwargs)
        help_texts = {
            "level": "سطح اهمیت این لاگ",
            "log_type": "دسته‌بندی نوع لاگ",
            "module": "نام ماژول یا فایل مبدأ",
            "method": "نام متد یا تابع",
            "message": "متن پیام لاگ",
            "resolution_note": "توضیحات مربوط به حل مسئله",
            "tags": "برچسب‌ها برای جستجوی آسان‌تر",
        }
        for field, help_text in help_texts.items():
            if field in form.base_fields:
                form.base_fields[field].help_text = help_text
        return form

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related("user")

    class Media:
        css = {"all": ("admin/css/monitoring_admin.css",)}
        js = ("admin/js/monitoring_admin.js",)
