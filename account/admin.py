"""
Account Module Admin
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseAdminModel

from account.models import User

# Register your models here.


class UserAdmin(BaseAdminModel):
    """Persian User Admin Interface"""

    list_display = ["fullName", "phone", "is_active", "last_login"]
    list_editable = ["is_active"]
    readonly_fields = ["last_login"]
    list_display_links = ["fullName", "phone"]
    ordering = ["id"]

    list_filter = ["is_active", "is_staff"]
    search_fields = ["phone"]

    fieldsets = (
        ("اطلاعات عمومی", {"fields": ("fullName", "phone", "password")}),
        (
            "مجوزها و دسترسی‌ها",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("تاریخ‌های مهم", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        ("اطلاعات عمومی", {"fields": ("fullName", "phone", "password1", "password2")}),
        (
            "مجوزها و دسترسی‌ها",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )

    # Persian display methods
    def get_form(self, request, obj=None, **kwargs):
        """Customize form with Persian help texts"""
        form = super().get_form(request, obj, **kwargs)
        if "fullName" in form.base_fields:
            form.base_fields["fullName"].help_text = "نام کامل کاربر را وارد کنید"
        if "phone" in form.base_fields:
            form.base_fields["phone"].help_text = "شماره تلفن همراه کاربر"
        return form


admin.site.register(User, UserAdmin)
