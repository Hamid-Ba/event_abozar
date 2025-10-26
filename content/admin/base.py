"""
Base Admin Configuration
Common admin functionality for content models
"""
from django.contrib import admin
from django.utils.html import format_html


class BaseContentAdmin(admin.ModelAdmin):
    """
    Base admin configuration for content models
    """

    list_display = ["title", "display_view_count", "publish_date", "created_at"]
    list_filter = ["publish_date", "created_at", "tags"]
    search_fields = ["title", "description"]
    ordering = ["-publish_date"]
    readonly_fields = ["created_at", "updated_at", "view_count"]
    list_per_page = 20
    date_hierarchy = "publish_date"
    save_on_top = True

    # Persian field names
    list_display_links = ["title"]
    empty_value_display = "تعریف نشده"

    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("title", "description", "image")}),
        ("انتشار", {"fields": ("publish_date", "tags")}),
        (
            "آمار",
            {"fields": ("view_count",), "classes": ("collapse",)},
        ),
        (
            "زمان‌بندی",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    # Persian actions
    actions_on_top = True
    actions_on_bottom = False

    def display_view_count(self, obj):
        """نمایش تعداد بازدید"""
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">👁 {}</span>',
            obj.view_count,
        )

    display_view_count.short_description = "بازدید"
    display_view_count.admin_order_field = "view_count"

    def get_queryset(self, request):
        """Optimize queryset with prefetch"""
        return super().get_queryset(request).prefetch_related("tags")
