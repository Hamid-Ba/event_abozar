"""
Education Admin Configuration
"""
from django.contrib import admin
from django.utils.html import format_html
from .base import BaseContentAdmin
from content.models import Education


@admin.register(Education)
class EducationAdmin(BaseContentAdmin):
    """
    Admin configuration for Education model - Persian Interface
    """

    # Persian customizations for Education
    list_display = [
        "title",
        "publish_date",
        "display_media_status",
        "tag_count",
        "created_at",
    ]
    list_filter = ["publish_date", "created_at", "tags"]

    fieldsets = (
        (
            "اطلاعات اصلی",
            {"fields": ("title", "description", "image", "publish_date", "tags")},
        ),
        (
            "فایل‌های آموزشی",
            {
                "fields": ("video", "document"),
                "description": "فایل‌های ویدیویی و اسنادی مرتبط با محتوای آموزشی",
            },
        ),
        ("تاریخچه", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    readonly_fields = ["created_at", "updated_at"]

    def display_media_status(self, obj):
        """Display media files status"""
        status_parts = []

        if obj.has_video:
            status_parts.append(
                '<span style="background-color: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">🎬 ویدیو</span>'
            )

        if obj.has_document:
            status_parts.append(
                '<span style="background-color: #007bff; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">📄 سند</span>'
            )

        if not status_parts:
            return '<span style="color: #999;">بدون فایل</span>'

        return format_html(" ".join(status_parts))

    display_media_status.short_description = "فایل‌های پیوست"

    def tag_count(self, obj):
        """Display tag count in Persian"""
        count = obj.tags.count()
        return f"{count} برچسب" if count > 0 else "بدون برچسب"

    tag_count.short_description = "تعداد برچسب‌ها"
    tag_count.admin_order_field = "tags__count"

    def get_form(self, request, obj=None, **kwargs):
        """Customize form with Persian help texts"""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["title"].help_text = "عنوان مطلب آموزشی را وارد کنید"
        form.base_fields["description"].help_text = "توضیحات کامل مطلب آموزشی"
        form.base_fields["publish_date"].help_text = "تاریخ انتشار مطلب آموزشی"

        if "video" in form.base_fields:
            form.base_fields[
                "video"
            ].help_text = "فایل ویدیوی آموزشی (فرمت‌های مجاز: mp4, avi, mov, mkv, wmv - حداکثر 500 مگابایت)"

        if "document" in form.base_fields:
            form.base_fields[
                "document"
            ].help_text = "فایل آموزشی PDF یا PowerPoint (فرمت‌های مجاز: pdf, ppt, pptx - حداکثر 50 مگابایت)"

        return form
