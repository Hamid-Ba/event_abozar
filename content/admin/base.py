"""
Base Admin Configuration
Common admin functionality for content models
"""
from django.contrib import admin


class BaseContentAdmin(admin.ModelAdmin):
    """
    Base admin configuration for content models
    """

    list_display = ["title", "publish_date", "created_at"]
    list_filter = ["publish_date", "created_at", "tags"]
    search_fields = ["title", "description"]
    ordering = ["-publish_date"]
    readonly_fields = ["created_at", "updated_at"]
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
            "زمان‌بندی",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    # Persian actions
    actions_on_top = True
    actions_on_bottom = False

    def get_queryset(self, request):
        """Optimize queryset with prefetch"""
        return super().get_queryset(request).prefetch_related("tags")
