"""
Festival Model
جشنواره / رویداد - هر جشنواره بازه ثبت‌نام خودش را دارد و چند جشنواره می‌توانند هم‌زمان برگزار شوند
"""
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from .categories import FestivalFormat, FestivalTopic, FestivalSpecialSection


class FestivalQuerySet(models.QuerySet):
    def open(self):
        """جشنواره‌های فعالی که الان بازه ثبت‌نامشان باز است"""
        now = timezone.now()
        return self.filter(
            is_active=True, registration_start__lte=now, registration_end__gte=now
        )

    def archived(self):
        """جشنواره‌هایی که مهلت ثبت‌نامشان تمام شده است"""
        return self.filter(registration_end__lt=timezone.now())

    def not_archived(self):
        """جشنواره‌های فعال که هنوز مهلتشان تمام نشده (باز یا به‌زودی)"""
        return self.filter(is_active=True, registration_end__gte=timezone.now())

    def featured(self):
        """جشنواره‌هایی که مدیر برای نمایش در صفحه اول تیک زده است"""
        return self.not_archived().filter(is_featured=True)


class Festival(models.Model):
    """جشنواره"""

    STATUS_UPCOMING = "upcoming"
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"

    title = models.CharField(max_length=255, verbose_name="عنوان")
    slug = models.SlugField(
        max_length=255, unique=True, allow_unicode=True, verbose_name="اسلاگ"
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")
    banner = models.ImageField(
        upload_to="festival/banners/", blank=True, null=True, verbose_name="بنر"
    )

    registration_start = models.DateTimeField(verbose_name="شروع ثبت‌نام")
    registration_end = models.DateTimeField(verbose_name="پایان ثبت‌نام")

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="جشنواره غیرفعال برای بازدیدکنندگان نمایش داده نمی‌شود",
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="نمایش در صفحه اول",
        help_text="مستقل از تاریخ؛ فقط جشنواره‌های فعال و تمام‌نشده نمایش داده می‌شوند",
    )
    display_order = models.IntegerField(
        default=0, verbose_name="ترتیب نمایش", help_text="عدد کمتر، بالاتر نمایش داده می‌شود"
    )

    required_judges = models.PositiveSmallIntegerField(
        default=3,
        verbose_name="تعداد داور لازم برای هر اثر",
        help_text="برای مرحله داوری",
    )

    max_score = models.PositiveSmallIntegerField(
        default=100,
        verbose_name="سقف امتیاز هر داور",
        help_text="هر داور به هر اثر امتیازی بین ۰ تا این عدد می‌دهد؛ امتیاز نهایی اثر مجموع امتیاز داوران است",
    )

    # اگر خالی باشد همه موارد فعال در دسترس است
    formats = models.ManyToManyField(
        FestivalFormat,
        blank=True,
        related_name="festivals",
        verbose_name="قالب‌های این جشنواره",
        help_text="اگر خالی باشد، همه قالب‌های فعال مجاز است",
    )
    topics = models.ManyToManyField(
        FestivalTopic,
        blank=True,
        related_name="festivals",
        verbose_name="محورهای این جشنواره",
        help_text="اگر خالی باشد، همه محورهای فعال مجاز است",
    )
    special_sections = models.ManyToManyField(
        FestivalSpecialSection,
        blank=True,
        related_name="festivals",
        verbose_name="بخش‌های ویژه این جشنواره",
        help_text="اگر خالی باشد، همه بخش‌های ویژه فعال مجاز است",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = FestivalQuerySet.as_manager()

    class Meta:
        verbose_name = "جشنواره"
        verbose_name_plural = "جشنواره‌ها"
        ordering = ["display_order", "-registration_start"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def status(self):
        now = timezone.now()
        if not self.is_active:
            return self.STATUS_CLOSED
        if now < self.registration_start:
            return self.STATUS_UPCOMING
        if now > self.registration_end:
            return self.STATUS_CLOSED
        return self.STATUS_OPEN

    @property
    def is_open(self):
        return self.status == self.STATUS_OPEN

    @property
    def is_archived(self):
        return timezone.now() > self.registration_end

    def allowed_formats(self):
        qs = self.formats.filter(is_active=True)
        return qs if self.pk and self.formats.exists() else FestivalFormat.objects.filter(is_active=True)

    def allowed_topics(self):
        qs = self.topics.filter(is_active=True)
        return qs if self.pk and self.topics.exists() else FestivalTopic.objects.filter(is_active=True)

    def allowed_special_sections(self):
        qs = self.special_sections.filter(is_active=True)
        return (
            qs
            if self.pk and self.special_sections.exists()
            else FestivalSpecialSection.objects.filter(is_active=True)
        )
