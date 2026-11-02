import django.db.models.deletion
from django.db import migrations, models

import festival.models.work


class Migration(migrations.Migration):
    """
    جشنواره چندتایی + اثر چندفایلی.

    فقط افزودنی/آزادسازی است (ستون جدید، nullable کردن ستون قدیمی) تا نسخه قبلی کد
    هم حین دیپلوی بدون خطا روی همین دیتابیس کار کند.
    """

    dependencies = [
        ("festival", "0009_work_publish_link"),
    ]

    operations = [
        migrations.CreateModel(
            name="Festival",
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
                (
                    "slug",
                    models.SlugField(
                        allow_unicode=True,
                        max_length=255,
                        unique=True,
                        verbose_name="اسلاگ",
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="توضیحات"),
                ),
                (
                    "banner",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="festival/banners/",
                        verbose_name="بنر",
                    ),
                ),
                (
                    "registration_start",
                    models.DateTimeField(verbose_name="شروع ثبت‌نام"),
                ),
                (
                    "registration_end",
                    models.DateTimeField(verbose_name="پایان ثبت‌نام"),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="جشنواره غیرفعال برای بازدیدکنندگان نمایش داده نمی‌شود",
                        verbose_name="فعال",
                    ),
                ),
                (
                    "is_featured",
                    models.BooleanField(
                        default=False,
                        help_text="مستقل از تاریخ؛ فقط جشنواره‌های فعال و تمام‌نشده نمایش داده می‌شوند",
                        verbose_name="نمایش در صفحه اول",
                    ),
                ),
                (
                    "display_order",
                    models.IntegerField(
                        default=0,
                        help_text="عدد کمتر، بالاتر نمایش داده می‌شود",
                        verbose_name="ترتیب نمایش",
                    ),
                ),
                (
                    "required_judges",
                    models.PositiveSmallIntegerField(
                        default=3,
                        help_text="برای مرحله داوری",
                        verbose_name="تعداد داور لازم برای هر اثر",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "formats",
                    models.ManyToManyField(
                        blank=True,
                        help_text="اگر خالی باشد، همه قالب‌های فعال مجاز است",
                        related_name="festivals",
                        to="festival.festivalformat",
                        verbose_name="قالب‌های این جشنواره",
                    ),
                ),
                (
                    "special_sections",
                    models.ManyToManyField(
                        blank=True,
                        help_text="اگر خالی باشد، همه بخش‌های ویژه فعال مجاز است",
                        related_name="festivals",
                        to="festival.festivalspecialsection",
                        verbose_name="بخش‌های ویژه این جشنواره",
                    ),
                ),
                (
                    "topics",
                    models.ManyToManyField(
                        blank=True,
                        help_text="اگر خالی باشد، همه محورهای فعال مجاز است",
                        related_name="festivals",
                        to="festival.festivaltopic",
                        verbose_name="محورهای این جشنواره",
                    ),
                ),
            ],
            options={
                "verbose_name": "جشنواره",
                "verbose_name_plural": "جشنواره‌ها",
                "ordering": ["display_order", "-registration_start"],
            },
        ),
        migrations.AddField(
            model_name="festivalregistration",
            name="festival",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registrations",
                to="festival.festival",
                verbose_name="جشنواره",
            ),
        ),
        migrations.AlterField(
            model_name="festivalregistration",
            name="festival_format",
            field=models.ForeignKey(
                blank=True,
                help_text="منسوخ: قالب اکنون روی هر اثر ثبت می‌شود",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registrations",
                to="festival.festivalformat",
                verbose_name="قالب جشنواره",
            ),
        ),
        migrations.AlterField(
            model_name="festivalregistration",
            name="festival_topic",
            field=models.ForeignKey(
                blank=True,
                help_text="منسوخ: محور اکنون روی هر اثر ثبت می‌شود",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registrations",
                to="festival.festivaltopic",
                verbose_name="محور جشنواره",
            ),
        ),
        migrations.AddConstraint(
            model_name="festivalregistration",
            constraint=models.UniqueConstraint(
                condition=models.Q(("festival__isnull", False)),
                fields=("user", "festival"),
                name="unique_registration_per_user_festival",
            ),
        ),
        migrations.AddField(
            model_name="work",
            name="festival_format",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="works",
                to="festival.festivalformat",
                verbose_name="قالب",
            ),
        ),
        migrations.AddField(
            model_name="work",
            name="festival_topic",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="works",
                to="festival.festivaltopic",
                verbose_name="محور",
            ),
        ),
        migrations.AddField(
            model_name="work",
            name="special_section",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="works",
                to="festival.festivalspecialsection",
                verbose_name="بخش ویژه",
            ),
        ),
        migrations.AddField(
            model_name="work",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "پیش‌نویس (بدون فایل)"),
                    ("submitted", "ارسال‌شده"),
                    ("under_review", "در حال داوری"),
                    ("judged", "داوری‌شده"),
                ],
                db_index=True,
                default="draft",
                max_length=20,
                verbose_name="وضعیت",
            ),
        ),
        migrations.AlterField(
            model_name="work",
            name="file",
            field=models.FileField(
                blank=True,
                help_text="منسوخ: از WorkFile استفاده کنید",
                upload_to=festival.models.work.work_file_upload_path,
                verbose_name="فایل (منسوخ)",
            ),
        ),
        migrations.CreateModel(
            name="WorkFile",
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
                    "file",
                    models.FileField(
                        upload_to=festival.models.work.work_file_item_upload_path,
                        verbose_name="فایل",
                    ),
                ),
                (
                    "original_name",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="نام اصلی فایل"
                    ),
                ),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("video", "ویدیو"),
                            ("audio", "صوت"),
                            ("image", "تصویر"),
                            ("document", "سند"),
                            ("archive", "فایل فشرده"),
                        ],
                        max_length=20,
                        verbose_name="نوع",
                    ),
                ),
                (
                    "size",
                    models.BigIntegerField(default=0, verbose_name="حجم (بایت)"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد"),
                ),
                (
                    "work",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="files",
                        to="festival.work",
                        verbose_name="اثر",
                    ),
                ),
            ],
            options={
                "verbose_name": "فایل اثر",
                "verbose_name_plural": "فایل‌های اثر",
                "ordering": ["created_at", "id"],
            },
        ),
    ]
