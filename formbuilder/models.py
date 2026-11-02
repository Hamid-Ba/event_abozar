"""
Form builder
فرم‌ساز ساده برای نظرسنجی (شرکت‌کننده/داور) و فرم داوری (معیارها = سؤال‌های امتیازی)
"""
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from festival.models import Festival, FestivalRegistration, Work


class Form(models.Model):
    KIND_SURVEY = "survey"
    KIND_JUDGING = "judging"
    KIND_CHOICES = [
        (KIND_SURVEY, "نظرسنجی"),
        (KIND_JUDGING, "فرم داوری"),
    ]

    AUDIENCE_PARTICIPANT = "participant"
    AUDIENCE_JUDGE = "judge"
    AUDIENCE_BOTH = "both"
    AUDIENCE_CHOICES = [
        (AUDIENCE_PARTICIPANT, "شرکت‌کنندگان"),
        (AUDIENCE_JUDGE, "داوران"),
        (AUDIENCE_BOTH, "هر دو"),
    ]

    festival = models.ForeignKey(
        Festival,
        on_delete=models.CASCADE,
        related_name="forms",
        null=True,
        blank=True,
        verbose_name="جشنواره",
        help_text="خالی = برای همهٔ جشنواره‌ها",
    )
    title = models.CharField(max_length=255, verbose_name="عنوان")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    kind = models.CharField(
        max_length=20, choices=KIND_CHOICES, default=KIND_SURVEY, verbose_name="نوع"
    )
    audience = models.CharField(
        max_length=20,
        choices=AUDIENCE_CHOICES,
        default=AUDIENCE_PARTICIPANT,
        verbose_name="مخاطب",
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    opens_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان باز شدن")
    closes_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان بسته شدن")
    is_anonymous = models.BooleanField(
        default=False,
        verbose_name="ناشناس",
        help_text="هویت پاسخ‌دهنده در گزارش مدیر نمایش داده نمی‌شود",
    )
    notified_at = models.DateTimeField(
        null=True, blank=True, editable=False, verbose_name="زمان ارسال اعلان باز شدن"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "فرم"
        verbose_name_plural = "فرم‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_open(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.opens_at and now < self.opens_at:
            return False
        if self.closes_at and now > self.closes_at:
            return False
        return True

    def clean(self):
        if self.kind == self.KIND_JUDGING:
            if self.festival_id is None:
                raise ValidationError({"festival": "فرم داوری باید به یک جشنواره وصل باشد."})
            clash = Form.objects.filter(
                festival_id=self.festival_id, kind=self.KIND_JUDGING, is_active=True
            ).exclude(pk=self.pk)
            if self.is_active and clash.exists():
                raise ValidationError(
                    "برای هر جشنواره فقط یک فرم داوری فعال می‌تواند وجود داشته باشد."
                )
        if self.opens_at and self.closes_at and self.closes_at <= self.opens_at:
            raise ValidationError({"closes_at": "زمان بسته شدن باید بعد از زمان باز شدن باشد."})

    def save(self, *args, **kwargs):
        if self.kind == self.KIND_JUDGING:
            self.audience = self.AUDIENCE_JUDGE
            self.is_anonymous = False
        super().save(*args, **kwargs)


class Question(models.Model):
    TYPE_SHORT_TEXT = "short_text"
    TYPE_LONG_TEXT = "long_text"
    TYPE_SINGLE_CHOICE = "single_choice"
    TYPE_MULTI_CHOICE = "multi_choice"
    TYPE_RATING = "rating"
    TYPE_FILE = "file"
    TYPE_CHOICES = [
        (TYPE_SHORT_TEXT, "متن کوتاه"),
        (TYPE_LONG_TEXT, "متن بلند"),
        (TYPE_SINGLE_CHOICE, "تک‌انتخابی"),
        (TYPE_MULTI_CHOICE, "چندانتخابی"),
        (TYPE_RATING, "امتیاز"),
        (TYPE_FILE, "فایل"),
    ]

    form = models.ForeignKey(
        Form, on_delete=models.CASCADE, related_name="questions", verbose_name="فرم"
    )
    text = models.CharField(max_length=500, verbose_name="متن سؤال")
    help_text = models.CharField(max_length=500, blank=True, verbose_name="راهنما")
    qtype = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="نوع سؤال")
    required = models.BooleanField(default=True, verbose_name="الزامی")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    choices = models.JSONField(
        default=list,
        blank=True,
        verbose_name="گزینه‌ها",
        help_text='برای تک‌انتخابی/چندانتخابی: فهرستی از متن گزینه‌ها، مثلاً ["عالی", "خوب"]',
    )
    min_value = models.PositiveSmallIntegerField(
        default=1, verbose_name="حداقل امتیاز", help_text="فقط برای سؤال امتیازی"
    )
    max_value = models.PositiveSmallIntegerField(
        default=5, verbose_name="حداکثر امتیاز", help_text="فقط برای سؤال امتیازی"
    )

    class Meta:
        verbose_name = "سؤال"
        verbose_name_plural = "سؤال‌ها"
        ordering = ["order", "id"]

    def __str__(self):
        return self.text

    def clean(self):
        if self.qtype in (self.TYPE_SINGLE_CHOICE, self.TYPE_MULTI_CHOICE):
            if not isinstance(self.choices, list) or len(self.choices) < 2:
                raise ValidationError({"choices": "برای سؤال انتخابی حداقل دو گزینه لازم است."})
            if not all(isinstance(c, str) and c.strip() for c in self.choices):
                raise ValidationError({"choices": "گزینه‌ها باید متن غیرخالی باشند."})
        if self.qtype == self.TYPE_RATING and self.min_value >= self.max_value:
            raise ValidationError({"max_value": "حداکثر امتیاز باید بیشتر از حداقل باشد."})


def answer_file_upload_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    name = uuid.uuid4().hex + (f".{ext}" if ext else "")
    return f"formbuilder/answers/{timezone.now():%Y/%m/%d}/{name}"


class Submission(models.Model):
    form = models.ForeignKey(
        Form, on_delete=models.CASCADE, related_name="submissions", verbose_name="فرم"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="form_submissions",
        verbose_name="پاسخ‌دهنده",
    )
    # فقط برای فرم داوری: اثر مورد داوری
    work = models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="form_submissions",
        verbose_name="اثر",
    )
    registration = models.ForeignKey(
        FestivalRegistration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="form_submissions",
        verbose_name="ثبت‌نام",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")

    class Meta:
        verbose_name = "پاسخ فرم"
        verbose_name_plural = "پاسخ‌های فرم"
        ordering = ["-created_at"]
        constraints = [
            # نظرسنجی: یک پاسخ برای هر کاربر و فرم
            models.UniqueConstraint(
                fields=["form", "user"],
                condition=models.Q(work__isnull=True),
                name="unique_submission_per_form_user",
            ),
            # فرم داوری: یک پاسخ برای هر داور و اثر
            models.UniqueConstraint(
                fields=["form", "user", "work"],
                condition=models.Q(work__isnull=False),
                name="unique_submission_per_form_user_work",
            ),
        ]

    def __str__(self):
        return f"{self.form_id} / {self.user_id}"


class Answer(models.Model):
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="answers", verbose_name="پاسخ فرم"
    )
    question = models.ForeignKey(
        Question, on_delete=models.PROTECT, related_name="answers", verbose_name="سؤال"
    )
    value = models.JSONField(null=True, blank=True, verbose_name="مقدار")
    file = models.FileField(
        upload_to=answer_file_upload_path, null=True, blank=True, verbose_name="فایل"
    )

    class Meta:
        verbose_name = "پاسخ"
        verbose_name_plural = "پاسخ‌ها"
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "question"], name="unique_answer_per_question"
            )
        ]

    def __str__(self):
        return f"{self.question_id}: {self.value}"
