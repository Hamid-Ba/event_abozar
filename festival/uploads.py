"""
Work file upload rules
قوانین آپلود فایل آثار: نوع مجاز، سقف حجم برای هر نوع و پیام‌های فارسی روشن برای کاربر

سقف‌ها از settings خوانده می‌شود (FESTIVAL_UPLOAD_LIMITS_MB و FESTIVAL_MAX_FILES_PER_WORK)
تا بدون تغییر کد قابل تنظیم باشد.
"""
import os

from django.conf import settings

KIND_VIDEO = "video"
KIND_AUDIO = "audio"
KIND_IMAGE = "image"
KIND_DOCUMENT = "document"
KIND_ARCHIVE = "archive"

EXTENSION_KINDS = {
    ".mp4": KIND_VIDEO,
    ".avi": KIND_VIDEO,
    ".mov": KIND_VIDEO,
    ".mkv": KIND_VIDEO,
    ".wmv": KIND_VIDEO,
    ".mp3": KIND_AUDIO,
    ".wav": KIND_AUDIO,
    ".aac": KIND_AUDIO,
    ".flac": KIND_AUDIO,
    ".jpg": KIND_IMAGE,
    ".jpeg": KIND_IMAGE,
    ".png": KIND_IMAGE,
    ".gif": KIND_IMAGE,
    ".bmp": KIND_IMAGE,
    ".pdf": KIND_DOCUMENT,
    ".doc": KIND_DOCUMENT,
    ".docx": KIND_DOCUMENT,
    ".txt": KIND_DOCUMENT,
    ".rtf": KIND_DOCUMENT,
    ".zip": KIND_ARCHIVE,
    ".rar": KIND_ARCHIVE,
    ".7z": KIND_ARCHIVE,
}

KIND_LABELS = {
    KIND_VIDEO: "ویدیو",
    KIND_AUDIO: "صوت",
    KIND_IMAGE: "تصویر",
    KIND_DOCUMENT: "سند",
    KIND_ARCHIVE: "فایل فشرده",
}

DEFAULT_LIMITS_MB = {
    KIND_VIDEO: 100,
    KIND_AUDIO: 100,
    KIND_IMAGE: 30,
    KIND_DOCUMENT: 100,
    KIND_ARCHIVE: 100,
}
DEFAULT_MAX_FILES_PER_WORK = 5


def get_limits_mb():
    limits = dict(DEFAULT_LIMITS_MB)
    limits.update(getattr(settings, "FESTIVAL_UPLOAD_LIMITS_MB", {}) or {})
    return limits


def get_max_files_per_work():
    return getattr(settings, "FESTIVAL_MAX_FILES_PER_WORK", DEFAULT_MAX_FILES_PER_WORK)


def get_extension(filename):
    return os.path.splitext(filename or "")[1].lower()


def detect_kind(filename):
    """نوع فایل از روی پسوند؛ None اگر پسوند مجاز نباشد"""
    return EXTENSION_KINDS.get(get_extension(filename))


def format_size(size_bytes):
    """حجم به‌صورت خوانا (مگابایت/کیلوبایت) برای پیام خطا"""
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} مگابایت"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.0f} کیلوبایت"
    return f"{size_bytes} بایت"


def allowed_extensions_label():
    return "، ".join(sorted(ext.lstrip(".") for ext in EXTENSION_KINDS))


def upload_rules():
    """قوانین آپلود برای نمایش در فرانت (راهنمای زیر هر فیلد آپلود)"""
    limits = get_limits_mb()
    return {
        "max_files_per_work": get_max_files_per_work(),
        "kinds": [
            {
                "kind": kind,
                "label": KIND_LABELS[kind],
                "max_size_mb": limits[kind],
                "extensions": sorted(
                    ext.lstrip(".") for ext, k in EXTENSION_KINDS.items() if k == kind
                ),
            }
            for kind in (KIND_VIDEO, KIND_AUDIO, KIND_IMAGE, KIND_DOCUMENT, KIND_ARCHIVE)
        ],
    }


def validate_upload(uploaded_file):
    """
    فایل آپلودشده را بررسی می‌کند و (kind) را برمی‌گرداند.
    در صورت خطا ValueError با پیام فارسی روشن برای کاربر می‌دهد.
    """
    name = getattr(uploaded_file, "name", "") or ""
    display_name = os.path.basename(name)
    kind = detect_kind(name)
    if kind is None:
        raise ValueError(
            f"فرمت فایل «{display_name}» مجاز نیست. "
            f"فرمت‌های مجاز: {allowed_extensions_label()}"
        )

    size = uploaded_file.size
    if size == 0:
        raise ValueError(f"فایل «{display_name}» خالی است.")

    max_mb = get_limits_mb()[kind]
    if size > max_mb * 1024 * 1024:
        raise ValueError(
            f"حجم فایل «{display_name}» {format_size(size)} است؛ "
            f"حداکثر حجم مجاز برای {KIND_LABELS[kind]} {max_mb} مگابایت است. "
            "لطفاً فایل را فشرده‌تر کنید و دوباره بارگذاری کنید."
        )
    return kind
