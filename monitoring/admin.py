from django.contrib import admin

from .models import CodeLog


@admin.register(CodeLog)
class CodeLogAdmin(admin.ModelAdmin):
    list_display = (
        "level",
        "module",
        "method",
        "timestamp",
        "duration",
        "cpu_usage",
        "memory_usage",
    )
    list_filter = ("level", "module", "timestamp")
    search_fields = ("module", "method", "message")
    ordering = ("-timestamp",)
    readonly_fields = ("timestamp",)

    fieldsets = (
        (
            None,
            {
                "fields": ("level", "module", "method", "message", "context"),
            },
        ),
        (
            "System Info",
            {
                "fields": ("duration", "cpu_usage", "memory_usage"),
            },
        ),
    )
