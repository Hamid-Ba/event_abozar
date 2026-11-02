"""
Judging Admin
مدیریت داوران و امتیازها
"""
from django.contrib import admin

from festival.models import JudgeProfile, Review


@admin.register(JudgeProfile)
class JudgeProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "festivals_list", "reviews_done")
    list_filter = ("is_active", "festivals")
    search_fields = ("user__phone", "user__fullName")
    filter_horizontal = ("festivals",)
    raw_id_fields = ("user",)

    @admin.display(description="جشنواره‌ها")
    def festivals_list(self, obj):
        return "، ".join(f.title for f in obj.festivals.all()) or "-"

    @admin.display(description="تعداد امتیازهای ثبت‌شده")
    def reviews_done(self, obj):
        return obj.user.festival_reviews.count()

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user").prefetch_related("festivals")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("work", "judge", "score", "created_at")
    list_filter = ("work__festival_registration__festival", "judge")
    search_fields = ("work__title", "judge__phone", "judge__fullName")
    raw_id_fields = ("work", "judge")
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("work", "judge")


class ReviewInline(admin.TabularInline):
    """ریز امتیاز داوران روی صفحهٔ اثر (فقط خواندنی)"""

    model = Review
    extra = 0
    can_delete = False
    fields = ("judge", "score", "note", "created_at")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False
