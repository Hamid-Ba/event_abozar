"""
Info Admin Configuration
Persian admin interface for ContactUs and other info models
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
from .models import ContactUs


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    """
    Persian admin interface for ContactUs model
    رابط مدیریت فارسی برای مدل تماس با ما
    """

    list_display = [
        "display_full_name",
        "display_phone",
        "display_email",
        "display_message_preview",
        "display_created_date",
        "display_status",
    ]

    list_filter = [
        "created_at",
    ]

    search_fields = ["full_name", "phone", "email", "message"]

    readonly_fields = ["created_at", "updated_at", "display_message_full"]

    fieldsets = (
        (
            "📞 اطلاعات تماس",
            {
                "fields": ("full_name", "phone", "email"),
                "description": "اطلاعات تماس ارسال‌کننده پیام",
            },
        ),
        (
            "💬 پیام",
            {
                "fields": ("display_message_full", "message"),
                "description": "متن پیام ارسال شده",
            },
        ),
        (
            "⏰ اطلاعات سیستم",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
                "description": "اطلاعات سیستمی",
            },
        ),
    )

    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    list_per_page = 25

    # Custom display methods
    def display_full_name(self, obj):
        """نمایش نام کامل با استایل"""
        return format_html('<strong style="color: #0066cc;">{}</strong>', obj.full_name)

    display_full_name.short_description = "نام کامل"
    display_full_name.admin_order_field = "full_name"

    def display_phone(self, obj):
        """نمایش شماره تلفن"""
        return format_html(
            '<span style="direction: ltr; font-family: monospace; background: #f8f9fa; padding: 2px 6px; border-radius: 3px;">{}</span>',
            obj.phone,
        )

    display_phone.short_description = "شماره تلفن"
    display_phone.admin_order_field = "phone"

    def display_email(self, obj):
        """نمایش ایمیل"""
        return format_html(
            '<a href="mailto:{}" style="color: #28a745;">{}</a>', obj.email, obj.email
        )

    display_email.short_description = "ایمیل"
    display_email.admin_order_field = "email"

    def display_message_preview(self, obj):
        """نمایش پیش‌نمایش پیام"""
        preview = obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
        return format_html(
            '<span title="{}" style="background: #e9ecef; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            obj.message,
            preview,
        )

    display_message_preview.short_description = "پیش‌نمایش پیام"

    def display_message_full(self, obj):
        """نمایش کامل پیام"""
        if obj.pk:
            return format_html(
                """
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border: 1px solid #dee2e6; max-width: 600px;">
                    <h4 style="margin: 0 0 10px 0; color: #495057;">💬 متن کامل پیام</h4>
                    <p style="line-height: 1.6; margin: 0; white-space: pre-wrap;">{}</p>
                    <hr style="margin: 10px 0; border: none; border-top: 1px solid #dee2e6;">
                    <small style="color: #6c757d;">
                        📅 تاریخ: {} | 
                        📊 تعداد کاراکتر: {}
                    </small>
                </div>
                """,
                obj.message,
                obj.created_at.strftime("%Y/%m/%d %H:%M"),
                len(obj.message),
            )
        return "پیام پس از ذخیره نمایش داده می‌شود"

    display_message_full.short_description = "متن کامل پیام"

    def display_created_date(self, obj):
        """نمایش تاریخ ایجاد"""
        return obj.created_at.strftime("%Y/%m/%d %H:%M")

    display_created_date.short_description = "تاریخ دریافت"
    display_created_date.admin_order_field = "created_at"

    def display_status(self, obj):
        """نمایش وضعیت براساس تاریخ"""
        now = timezone.now()
        if obj.created_at >= now - timedelta(hours=1):
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">🔥 جدید</span>'
            )
        elif obj.created_at >= now - timedelta(days=1):
            return format_html(
                '<span style="background-color: #ffc107; color: #212529; padding: 2px 6px; border-radius: 3px; font-size: 10px;">⏰ امروز</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">📅 قدیمی</span>'
            )

    display_status.short_description = "وضعیت"

    def get_readonly_fields(self, request, obj=None):
        """تنظیم فیلدهای فقط خواندنی"""
        readonly_fields = list(self.readonly_fields)
        if obj:  # editing existing object
            readonly_fields.extend(["full_name", "phone", "email"])
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        """محدود کردن حذف پیام‌ها"""
        return request.user.is_superuser

    def has_add_permission(self, request):
        """غیرفعال کردن اضافه کردن دستی"""
        return False  # Contact messages should only come via API

    actions = ["mark_as_read"]

    def mark_as_read(self, request, queryset):
        """علامت‌گذاری به عنوان خوانده شده"""
        count = queryset.count()
        # In future, we can add a 'read' field to track this
        self.message_user(request, f"{count} پیام علامت‌گذاری شد")

    mark_as_read.short_description = "علامت‌گذاری به عنوان خوانده شده"
