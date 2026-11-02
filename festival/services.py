"""
Festival Registration Services
"""
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import serializers, status
from rest_framework.exceptions import APIException

from festival.models import Festival, FestivalRegistration, Work, WorkFile
from festival.uploads import get_max_files_per_work, validate_upload

User = get_user_model()


class FestivalClosed(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "مهلت ثبت‌نام و ارسال اثر در این جشنواره به پایان رسیده یا هنوز آغاز نشده است."
    default_code = "festival_closed"


class AlreadyRegistered(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "شما قبلاً در این جشنواره ثبت‌نام کرده‌اید. اطلاعات ثبت‌نامتان را ویرایش کنید و اثر جدید اضافه کنید."
    default_code = "already_registered"

    def __init__(self, registration_id=None):
        super().__init__()
        self.detail = {
            "detail": self.default_detail,
            "message": self.default_detail,
            "code": self.default_code,
            "registration_id": registration_id,
        }


class WorkLocked(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "این اثر وارد مرحله داوری شده و دیگر قابل ویرایش یا حذف نیست."
    default_code = "work_locked"


def ensure_festival_open(festival):
    """ثبت‌نام/ارسال اثر فقط در بازهٔ باز جشنواره مجاز است (ثبت‌نام‌های قدیمی بدون جشنواره آزادند)"""
    if festival is not None and not festival.is_open:
        raise FestivalClosed()


def ensure_work_editable(work):
    ensure_festival_open(work.festival_registration.festival)
    if work.status in (Work.STATUS_UNDER_REVIEW, Work.STATUS_JUDGED):
        raise WorkLocked()


def get_sole_open_festival():
    """برای کلاینت‌های قدیمی که جشنواره نمی‌فرستند: اگر دقیقاً یک جشنواره باز باشد همان"""
    open_festivals = list(Festival.objects.open()[:2])
    if len(open_festivals) == 1:
        return open_festivals[0]
    return None


@transaction.atomic
def create_festival_registration(phone_number, registration_data):
    """
    Create or get user by phone number and create festival registration
    """
    # Get or create user by phone number
    user, created = User.objects.get_or_create(phone=phone_number)

    # If user is new, we can set some basic info from registration data
    if created or not user.fullName:
        user.fullName = registration_data.get("full_name", "")
        user.save()

    return create_registration_for_user(user, registration_data), created


def create_registration_for_user(user, registration_data):
    """یک ثبت‌نام برای هر کاربر در هر جشنواره؛ تکراری ۴۰۹ می‌دهد"""
    festival = registration_data.get("festival")
    if festival is not None:
        existing = FestivalRegistration.objects.filter(
            user=user, festival=festival
        ).first()
        if existing:
            raise AlreadyRegistered(existing.id)
    try:
        with transaction.atomic():
            return FestivalRegistration.objects.create(user=user, **registration_data)
    except IntegrityError:
        # دو درخواست هم‌زمان
        existing = FestivalRegistration.objects.filter(
            user=user, festival=festival
        ).first()
        if existing is None:
            raise  # خطای دیگری است (مثلاً فیلد اجباری خالی)، نه ثبت‌نام تکراری
        raise AlreadyRegistered(existing.id)


def validate_new_files(uploaded_files, existing_count=0):
    """
    فایل‌های جدید را پیش از ذخیره بررسی می‌کند (تعداد، نوع، حجم).
    نوع هر فایل را برمی‌گرداند. خطا: ValidationError فارسی روی کلید files.
    """
    max_files = get_max_files_per_work()
    if existing_count + len(uploaded_files) > max_files:
        raise serializers.ValidationError(
            {
                "files": [
                    f"هر اثر حداکثر {max_files} فایل می‌تواند داشته باشد "
                    f"(این اثر الان {existing_count} فایل دارد و {len(uploaded_files)} فایل دیگر ارسال کرده‌اید)."
                ]
            }
        )
    kinds = []
    for uploaded in uploaded_files:
        try:
            kinds.append(validate_upload(uploaded))
        except ValueError as exc:
            raise serializers.ValidationError({"files": [str(exc)]})
    return kinds


def attach_files(work, uploaded_files):
    """فایل‌ها را به اثر وصل می‌کند و وضعیت اثر را به‌روز می‌کند"""
    if not uploaded_files:
        return []
    kinds = validate_new_files(uploaded_files, existing_count=work.files.count())
    created = [
        WorkFile.objects.create(
            work=work,
            file=uploaded,
            original_name=uploaded.name[:255],
            kind=kind,
            size=uploaded.size,
        )
        for uploaded, kind in zip(uploaded_files, kinds)
    ]
    if work.status == Work.STATUS_DRAFT:
        work.status = Work.STATUS_SUBMITTED
        work.save(update_fields=["status", "updated_at"])
    return created


def refresh_work_status_after_file_removal(work):
    """اگر آخرین فایل اثر حذف شد، اثر دوباره پیش‌نویس می‌شود"""
    if work.status == Work.STATUS_SUBMITTED and not WorkFile.objects.filter(work=work).exists():
        work.status = Work.STATUS_DRAFT
        work.save(update_fields=["status", "updated_at"])
