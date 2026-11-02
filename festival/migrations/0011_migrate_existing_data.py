import os

from django.db import migrations
from django.utils import timezone

EXTENSION_KINDS = {
    ".mp4": "video",
    ".avi": "video",
    ".mov": "video",
    ".mkv": "video",
    ".wmv": "video",
    ".mp3": "audio",
    ".wav": "audio",
    ".aac": "audio",
    ".flac": "audio",
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".gif": "image",
    ".bmp": "image",
    ".pdf": "document",
    ".doc": "document",
    ".docx": "document",
    ".txt": "document",
    ".rtf": "document",
    ".zip": "archive",
    ".rar": "archive",
    ".7z": "archive",
}


def forwards(apps, schema_editor):
    Festival = apps.get_model("festival", "Festival")
    FestivalRegistration = apps.get_model("festival", "FestivalRegistration")
    Work = apps.get_model("festival", "Work")
    WorkFile = apps.get_model("festival", "WorkFile")

    # ثبت‌نام‌های موجود به یک جشنواره آرشیوشده («یازدهم») وصل می‌شوند.
    # جشنواره جدید را مدیر در پنل تعریف می‌کند.
    legacy = FestivalRegistration.objects.filter(festival__isnull=True)
    if legacy.exists():
        first = legacy.order_by("created_at").first()
        festival, _ = Festival.objects.get_or_create(
            slug="abouzar-11",
            defaults={
                "title": "یازدهمین جشنواره رسانه‌ای ابوذر",
                "registration_start": first.created_at,
                "registration_end": timezone.now(),
                "is_active": True,
                "is_featured": False,
            },
        )
        legacy.update(festival=festival)

    # قالب/محور/بخش ویژه از ثبت‌نام به اثر منتقل می‌شود
    for work in Work.objects.select_related("festival_registration").iterator():
        registration = work.festival_registration
        changed = []
        if work.festival_format_id is None and registration.festival_format_id:
            work.festival_format_id = registration.festival_format_id
            changed.append("festival_format")
        if work.festival_topic_id is None and registration.festival_topic_id:
            work.festival_topic_id = registration.festival_topic_id
            changed.append("festival_topic")
        if work.special_section_id is None and registration.special_section_id:
            work.special_section_id = registration.special_section_id
            changed.append("special_section")

        # فایل تکی قدیمی به WorkFile منتقل می‌شود
        if work.file and not WorkFile.objects.filter(work=work).exists():
            name = work.file.name
            try:
                size = work.file.size
            except Exception:
                size = 0
            ext = os.path.splitext(name)[1].lower()
            WorkFile.objects.create(
                work=work,
                file=name,
                original_name=os.path.basename(name),
                kind=EXTENSION_KINDS.get(ext, "document"),
                size=size,
            )
            work.status = "submitted"
            changed.append("status")

        if changed:
            work.save(update_fields=changed)


class Migration(migrations.Migration):
    dependencies = [("festival", "0010_festival_multi_work_files")]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
