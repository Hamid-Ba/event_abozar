import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import formbuilder.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("festival", "0013_notification"),
    ]

    operations = [
        migrations.CreateModel(
            name="Form",
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
                ("title", models.CharField(max_length=255, verbose_name="عنوان")),
                ("description", models.TextField(blank=True, verbose_name="توضیحات")),
                (
                    "kind",
                    models.CharField(
                        choices=[("survey", "نظرسنجی"), ("judging", "فرم داوری")],
                        default="survey",
                        max_length=20,
                        verbose_name="نوع",
                    ),
                ),
                (
                    "audience",
                    models.CharField(
                        choices=[
                            ("participant", "شرکت‌کنندگان"),
                            ("judge", "داوران"),
                            ("both", "هر دو"),
                        ],
                        default="participant",
                        max_length=20,
                        verbose_name="مخاطب",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                (
                    "opens_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="زمان باز شدن"
                    ),
                ),
                (
                    "closes_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="زمان بسته شدن"
                    ),
                ),
                (
                    "is_anonymous",
                    models.BooleanField(
                        default=False,
                        help_text="هویت پاسخ‌دهنده در گزارش مدیر نمایش داده نمی‌شود",
                        verbose_name="ناشناس",
                    ),
                ),
                (
                    "notified_at",
                    models.DateTimeField(
                        blank=True,
                        editable=False,
                        null=True,
                        verbose_name="زمان ارسال اعلان باز شدن",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "festival",
                    models.ForeignKey(
                        blank=True,
                        help_text="خالی = برای همهٔ جشنواره‌ها",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="forms",
                        to="festival.festival",
                        verbose_name="جشنواره",
                    ),
                ),
            ],
            options={
                "verbose_name": "فرم",
                "verbose_name_plural": "فرم‌ها",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Question",
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
                ("text", models.CharField(max_length=500, verbose_name="متن سؤال")),
                (
                    "help_text",
                    models.CharField(blank=True, max_length=500, verbose_name="راهنما"),
                ),
                (
                    "qtype",
                    models.CharField(
                        choices=[
                            ("short_text", "متن کوتاه"),
                            ("long_text", "متن بلند"),
                            ("single_choice", "تک‌انتخابی"),
                            ("multi_choice", "چندانتخابی"),
                            ("rating", "امتیاز"),
                            ("file", "فایل"),
                        ],
                        max_length=20,
                        verbose_name="نوع سؤال",
                    ),
                ),
                ("required", models.BooleanField(default=True, verbose_name="الزامی")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                (
                    "choices",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text='برای تک‌انتخابی/چندانتخابی: فهرستی از متن گزینه‌ها، مثلاً ["عالی", "خوب"]',
                        verbose_name="گزینه‌ها",
                    ),
                ),
                (
                    "min_value",
                    models.PositiveSmallIntegerField(
                        default=1,
                        help_text="فقط برای سؤال امتیازی",
                        verbose_name="حداقل امتیاز",
                    ),
                ),
                (
                    "max_value",
                    models.PositiveSmallIntegerField(
                        default=5,
                        help_text="فقط برای سؤال امتیازی",
                        verbose_name="حداکثر امتیاز",
                    ),
                ),
                (
                    "form",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="questions",
                        to="formbuilder.form",
                        verbose_name="فرم",
                    ),
                ),
            ],
            options={
                "verbose_name": "سؤال",
                "verbose_name_plural": "سؤال‌ها",
                "ordering": ["order", "id"],
            },
        ),
        migrations.CreateModel(
            name="Submission",
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
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال"),
                ),
                (
                    "form",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="formbuilder.form",
                        verbose_name="فرم",
                    ),
                ),
                (
                    "registration",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="form_submissions",
                        to="festival.festivalregistration",
                        verbose_name="ثبت‌نام",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="form_submissions",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="پاسخ‌دهنده",
                    ),
                ),
                (
                    "work",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="form_submissions",
                        to="festival.work",
                        verbose_name="اثر",
                    ),
                ),
            ],
            options={
                "verbose_name": "پاسخ فرم",
                "verbose_name_plural": "پاسخ‌های فرم",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Answer",
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
                    "value",
                    models.JSONField(blank=True, null=True, verbose_name="مقدار"),
                ),
                (
                    "file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=formbuilder.models.answer_file_upload_path,
                        verbose_name="فایل",
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="answers",
                        to="formbuilder.question",
                        verbose_name="سؤال",
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="formbuilder.submission",
                        verbose_name="پاسخ فرم",
                    ),
                ),
            ],
            options={"verbose_name": "پاسخ", "verbose_name_plural": "پاسخ‌ها"},
        ),
        migrations.AddConstraint(
            model_name="submission",
            constraint=models.UniqueConstraint(
                condition=models.Q(("work__isnull", True)),
                fields=("form", "user"),
                name="unique_submission_per_form_user",
            ),
        ),
        migrations.AddConstraint(
            model_name="submission",
            constraint=models.UniqueConstraint(
                condition=models.Q(("work__isnull", False)),
                fields=("form", "user", "work"),
                name="unique_submission_per_form_user_work",
            ),
        ),
        migrations.AddConstraint(
            model_name="answer",
            constraint=models.UniqueConstraint(
                fields=("submission", "question"), name="unique_answer_per_question"
            ),
        ),
    ]
