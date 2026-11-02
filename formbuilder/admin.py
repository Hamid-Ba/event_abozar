from django.contrib import admin

from formbuilder.models import Answer, Form, Question, Submission
from formbuilder.views import export_form_csv


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ("order", "text", "qtype", "required", "choices", "min_value", "max_value", "help_text")
    ordering = ("order", "id")


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "kind",
        "audience",
        "festival",
        "is_active",
        "opens_at",
        "closes_at",
        "questions_count",
        "submissions_count",
    )
    list_filter = ("kind", "audience", "festival", "is_active")
    search_fields = ("title", "description")
    inlines = [QuestionInline]
    actions = ["export_csv"]
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("title", "description", "festival", "kind", "audience")}),
        (
            "زمان‌بندی و وضعیت",
            {
                "fields": ("is_active", "opens_at", "closes_at", "is_anonymous"),
                "description": "فرم داوری: مخاطب همیشه «داوران» است و معیارها همان سؤال‌های «امتیاز»اند؛ امتیاز هر داور مجموع معیارهاست.",
            },
        ),
    )

    def get_queryset(self, request):
        from django.db.models import Count

        return (
            super()
            .get_queryset(request)
            .annotate(_questions=Count("questions", distinct=True), _submissions=Count("submissions", distinct=True))
        )

    @admin.display(description="تعداد سؤال", ordering="_questions")
    def questions_count(self, obj):
        return obj._questions

    @admin.display(description="تعداد پاسخ", ordering="_submissions")
    def submissions_count(self, obj):
        return obj._submissions

    @admin.action(description="خروجی CSV پاسخ‌های فرم‌های انتخابی (اولین فرم)")
    def export_csv(self, request, queryset):
        form = queryset.first()
        submissions = (
            Submission.objects.filter(form=form)
            .select_related("user", "work")
            .prefetch_related("answers")
        )
        return export_form_csv(form, submissions, request)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    can_delete = False
    fields = ("question", "value", "file")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("form", "display_user", "work", "created_at")
    list_filter = ("form", "form__kind")
    raw_id_fields = ("user", "work", "registration")
    readonly_fields = ("form", "user", "work", "registration", "created_at")
    inlines = [AnswerInline]

    @admin.display(description="پاسخ‌دهنده")
    def display_user(self, obj):
        return "ناشناس" if obj.form.is_anonymous else str(obj.user)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("form", "user", "work")

    def has_add_permission(self, request):
        return False
