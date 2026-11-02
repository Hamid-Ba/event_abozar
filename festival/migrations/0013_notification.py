import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("festival", "0012_judging"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("work_status", "تغییر وضعیت اثر"),
                            ("form_opened", "بازشدن نظرسنجی"),
                        ],
                        max_length=30,
                        verbose_name="نوع",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="عنوان")),
                ("body", models.TextField(blank=True, verbose_name="متن")),
                (
                    "object_id",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="شناسه مرتبط"
                    ),
                ),
                (
                    "is_read",
                    models.BooleanField(
                        db_index=True, default=False, verbose_name="خوانده‌شده"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="تاریخ"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="festival_notifications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="کاربر",
                    ),
                ),
            ],
            options={
                "verbose_name": "اعلان",
                "verbose_name_plural": "اعلان‌ها",
                "ordering": ["-created_at"],
            },
        ),
    ]
