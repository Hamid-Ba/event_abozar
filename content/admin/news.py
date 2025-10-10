"""
News Admin Configuration
"""
from django.contrib import admin
from .base import BaseContentAdmin
from content.models import News


@admin.register(News)
class NewsAdmin(BaseContentAdmin):
    """
    Admin configuration for News model - Persian Interface
    """

    # Persian customizations for News
    list_display = ["title", "publish_date", "tag_count", "created_at"]
    list_filter = ["publish_date", "created_at", "tags"]

    def tag_count(self, obj):
        """Display tag count in Persian"""
        count = obj.tags.count()
        return f"{count} برچسب" if count > 0 else "بدون برچسب"

    tag_count.short_description = "تعداد برچسب‌ها"
    tag_count.admin_order_field = "tags__count"

    def get_form(self, request, obj=None, **kwargs):
        """Customize form with Persian help texts"""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["title"].help_text = "عنوان خبر را وارد کنید"
        form.base_fields["description"].help_text = "توضیحات کامل خبر"
        form.base_fields["publish_date"].help_text = "تاریخ انتشار خبر"
        return form
