"""
Festival Registration Models
"""
from django.db import models
from django.contrib.auth import get_user_model
from province.models import Province, City

User = get_user_model()


class FestivalRegistration(models.Model):
    """Festival Registration Model for یازدهمین جشنواره رسانه ای ابوذر"""

    # Gender choices
    GENDER_CHOICES = [
        ("male", "مرد"),
        ("female", "زن"),
    ]

    # Festival format choices (قالب های جشنواره)
    FORMAT_CHOICES = [
        ("news_report", "گزارش خبری"),
        ("interview", "مصاحبه"),
        ("editorial", "یادداشت و سرمقاله"),
        ("headline", "تیتر"),
        ("infographic", "اینفوگرافی"),
        ("motion_graphic", "موشن گرافی"),
        ("photo", "عکس"),
        ("video_clip", "کلیپ و گزارش ویدیویی"),
        ("documentary", "مستند"),
        ("podcast", "پادکست"),
    ]

    # Festival topics choices (محورهای جشنواره)
    TOPIC_CHOICES = [
        ("year_slogan", "شعار سال"),
        ("jihad_explanation", "جهاد تبیین"),
        ("media_industry", "پیوند رسانه و صنعت"),
        ("social_harms", "مقابله با آسیب‌های اجتماعی"),
        ("revolution_achievements", "دستاوردهای انقلاب اسلامی"),
        ("basij_action", "بسیج و حوزه‌های اقدام"),
        ("hope_happiness", "امید و نشاط آفرینی"),
        ("family_society", "خانواده ،جامعه و فرزندآوری"),
        ("islamic_lifestyle", "سبک زندگی ایرانی اسلامی"),
        ("sacrifice_martyrdom", "ایثار و شهادت"),
        ("water_electricity_saving", "صرفه‌جویی در مصرف آب و برق"),
    ]

    # Special sections choices (بخش‌های ویژه)
    SPECIAL_SECTION_CHOICES = [
        ("progress_narrative", "روایت پیشرفت"),
        ("field_narrative_12days", "روایت میدان در جنگ ۱۲ روزه"),
    ]

    # User relationship
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="festival_registrations"
    )

    # Personal Information
    full_name = models.CharField(max_length=255, verbose_name="نام و نام خانوادگی")
    father_name = models.CharField(max_length=100, verbose_name="نام پدر")
    national_id = models.CharField(max_length=10, unique=True, verbose_name="کد ملی")
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, verbose_name="جنسیت"
    )
    education = models.CharField(max_length=255, verbose_name="تحصیلات")

    # Contact Information
    phone_number = models.CharField(max_length=11, verbose_name="شماره تماس")
    virtual_number = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="شماره مجازی"
    )
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, verbose_name="استان"
    )
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="شهر")

    # Media Information
    media_name = models.CharField(max_length=255, verbose_name="نام رسانه")

    # Festival Categories
    festival_format = models.CharField(
        max_length=50, choices=FORMAT_CHOICES, verbose_name="قالب جشنواره"
    )
    festival_topic = models.CharField(
        max_length=50, choices=TOPIC_CHOICES, verbose_name="محور جشنواره"
    )
    special_section = models.CharField(
        max_length=50,
        choices=SPECIAL_SECTION_CHOICES,
        blank=True,
        null=True,
        verbose_name="بخش ویژه",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ثبت نام جشنواره"
        verbose_name_plural = "ثبت نام های جشنواره"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.media_name}"
