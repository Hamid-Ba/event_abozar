import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """داوری: داور، امتیاز هر داور، امتیاز نهایی اثر (مجموع امتیازها)"""

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("festival", "0011_migrate_existing_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="festival",
            name="max_score",
            field=models.PositiveSmallIntegerField(
                default=100,
                help_text="هر داور به هر اثر امتیازی بین ۰ تا این عدد می‌دهد؛ امتیاز نهایی اثر مجموع امتیاز داوران است",
                verbose_name="سقف امتیاز هر داور",
            ),
        ),
        migrations.AddField(
            model_name="work",
            name="final_score",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                editable=False,
                help_text="مجموع امتیاز همهٔ داوران",
                max_digits=8,
                null=True,
                verbose_name="امتیاز نهایی",
            ),
        ),
        migrations.AddField(
            model_name="work",
            name="reviews_count",
            field=models.PositiveSmallIntegerField(
                default=0, editable=False, verbose_name="تعداد داوران امتیازدهنده"
            ),
        ),
        migrations.CreateModel(
            name="JudgeProfile",
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
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "festivals",
                    models.ManyToManyField(
                        blank=True,
                        help_text="داور فقط آثار این جشنواره‌ها را می‌بیند",
                        related_name="judges",
                        to="festival.festival",
                        verbose_name="جشنواره‌های قابل داوری",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="judge_profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="کاربر",
                    ),
                ),
            ],
            options={"verbose_name": "داور", "verbose_name_plural": "داوران"},
        ),
        migrations.CreateModel(
            name="Review",
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
                    "score",
                    models.DecimalField(
                        decimal_places=2, max_digits=6, verbose_name="امتیاز"
                    ),
                ),
                ("note", models.TextField(blank=True, verbose_name="یادداشت")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "judge",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="festival_reviews",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="داور",
                    ),
                ),
                (
                    "work",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="festival.work",
                        verbose_name="اثر",
                    ),
                ),
            ],
            options={
                "verbose_name": "امتیاز داور",
                "verbose_name_plural": "امتیازهای داوران",
                "ordering": ["created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="review",
            constraint=models.UniqueConstraint(
                fields=("work", "judge"), name="unique_review_per_work_judge"
            ),
        ),
    ]
