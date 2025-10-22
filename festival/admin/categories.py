"""
Admin configuration for Festival Category Models
پیکربندی مدیریت مدل‌های دسته‌بندی جشنواره
"""
from django.contrib import admin
from festival.models import FestivalFormat, FestivalTopic, FestivalSpecialSection


@admin.register(FestivalFormat)
class FestivalFormatAdmin(admin.ModelAdmin):
    """
    Admin interface for Festival Format
    رابط مدیریت قالب‌های جشنواره
    """

    list_display = ("name", "code", "is_active", "display_order", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "code", "description")
    ordering = ("display_order", "name")

    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("code", "name", "description")}),
        ("تنظیمات", {"fields": ("is_active", "display_order")}),
        ("تاریخچه", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    readonly_fields = ("created_at", "updated_at")

    class Meta:
        verbose_name = "قالب جشنواره"
        verbose_name_plural = "قالب‌های جشنواره"


@admin.register(FestivalTopic)
class FestivalTopicAdmin(admin.ModelAdmin):
    """
    Admin interface for Festival Topic
    رابط مدیریت محورهای جشنواره
    """

    list_display = ("name", "code", "is_active", "display_order", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "code", "description")
    ordering = ("display_order", "name")

    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("code", "name", "description")}),
        ("تنظیمات", {"fields": ("is_active", "display_order")}),
        ("تاریخچه", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    readonly_fields = ("created_at", "updated_at")

    class Meta:
        verbose_name = "محور جشنواره"
        verbose_name_plural = "محورهای جشنواره"


@admin.register(FestivalSpecialSection)
class FestivalSpecialSectionAdmin(admin.ModelAdmin):
    """
    Admin interface for Festival Special Section
    رابط مدیریت بخش‌های ویژه جشنواره
    """

    list_display = ("name", "code", "is_active", "display_order", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "code", "description")
    ordering = ("display_order", "name")

    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("code", "name", "description")}),
        ("تنظیمات", {"fields": ("is_active", "display_order")}),
        ("تاریخچه", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    readonly_fields = ("created_at", "updated_at")

    class Meta:
        verbose_name = "بخش ویژه"
        verbose_name_plural = "بخش‌های ویژه"
