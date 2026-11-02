"""
قرارداد خطای API

هر پاسخ خطا همان بدنهٔ قبلی DRF را نگه می‌دارد (تا فرانتِ فعلی نشکند) و یک کلید
`message` با جمله‌ای فارسی و قابل‌نمایش به کاربر به آن اضافه می‌شود:

    {"title": ["این فیلد الزامی است."], "message": "این فیلد الزامی است."}

برای خطاهای غیر از اعتبارسنجی (۴۰۱، ۴۰۳، ۴۰۴، ۴۱۳، ۵۰۰ و ...) هم همین `message` هست.
"""
import logging

from django.core.exceptions import (
    ObjectDoesNotExist,
    PermissionDenied,
    RequestDataTooBig,
    TooManyFieldsSent,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)

NOT_AUTHENTICATED_MESSAGE = "برای ادامه ابتدا وارد حساب کاربری شوید."
PERMISSION_MESSAGE = "شما دسترسی لازم برای این کار را ندارید."
NOT_FOUND_MESSAGE = "موردی با این مشخصات پیدا نشد."
TOO_LARGE_MESSAGE = "حجم فایل یا درخواست ارسالی بیش از حد مجاز است."
THROTTLED_MESSAGE = "تعداد درخواست‌ها زیاد است؛ کمی صبر کنید و دوباره تلاش کنید."
METHOD_NOT_ALLOWED_MESSAGE = "این روش درخواست برای این آدرس مجاز نیست."
UNSUPPORTED_MEDIA_MESSAGE = "نوع داده ارسالی پشتیبانی نمی‌شود."
SERVER_ERROR_MESSAGE = "خطای غیرمنتظره‌ای در سرور رخ داد. لطفاً دوباره تلاش کنید."
DEFAULT_VALIDATION_MESSAGE = "اطلاعات واردشده معتبر نیست."

# کدهای خطاهای عمومی DRF/simplejwt که پیام انگلیسی دارند
GENERIC_CODES = {
    "not_authenticated",
    "authentication_failed",
    "token_not_valid",
    "permission_denied",
    "not_found",
    "method_not_allowed",
    "unsupported_media_type",
    "throttled",
}


def _first_message(data):
    """اولین جملهٔ خطا را از هر ساختاری (str / list / dict) بیرون می‌کشد"""
    if isinstance(data, str):
        return data
    if isinstance(data, (list, tuple)):
        for item in data:
            message = _first_message(item)
            if message:
                return message
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "message":
                continue
            message = _first_message(value)
            if message:
                return message
    return ""


def _with_message(data, message):
    """بدنهٔ خطا را به‌صورت dict درمی‌آورد و message را اضافه می‌کند"""
    if isinstance(data, dict):
        body = dict(data)
    elif isinstance(data, list):
        body = {"non_field_errors": data}
    else:
        body = {"detail": data}
    body.setdefault("message", message)
    return body


def api_exception_handler(exc, context):
    # خطاهای جنگو که DRF نمی‌شناسد
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(
            exc.message_dict if hasattr(exc, "message_dict") else exc.messages
        )
    elif isinstance(exc, (RequestDataTooBig, TooManyFieldsSent)):
        return Response(
            {"detail": TOO_LARGE_MESSAGE, "message": TOO_LARGE_MESSAGE},
            status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )
    elif isinstance(exc, ObjectDoesNotExist) and not isinstance(exc, Http404):
        exc = Http404()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = drf_exception_handler(exc, context)
    if response is None:
        logger.exception("Unhandled API exception", exc_info=exc)
        return Response(
            {"detail": SERVER_ERROR_MESSAGE, "message": SERVER_ERROR_MESSAGE},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    code = response.status_code
    # فقط خطاهای عمومی DRF (انگلیسی) با جملهٔ فارسی عوض می‌شوند؛
    # خطاهای دامنه (مثل «مهلت ثبت‌نام تمام شده») پیام اختصاصی خودشان را نگه می‌دارند.
    generic = getattr(exc, "default_code", None) in GENERIC_CODES

    if generic and code == status.HTTP_401_UNAUTHORIZED:
        message = NOT_AUTHENTICATED_MESSAGE
    elif generic and code == status.HTTP_403_FORBIDDEN:
        message = PERMISSION_MESSAGE
    elif generic and code == status.HTTP_404_NOT_FOUND:
        message = NOT_FOUND_MESSAGE
    elif generic and code == status.HTTP_405_METHOD_NOT_ALLOWED:
        message = METHOD_NOT_ALLOWED_MESSAGE
    elif generic and code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE:
        message = UNSUPPORTED_MEDIA_MESSAGE
    elif generic and code == status.HTTP_429_TOO_MANY_REQUESTS:
        message = THROTTLED_MESSAGE
    elif code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE:
        message = _first_message(response.data) or TOO_LARGE_MESSAGE
    else:
        message = _first_message(response.data) or DEFAULT_VALIDATION_MESSAGE

    if generic:
        # دیتای انگلیسی پیش‌فرض DRF با جملهٔ فارسی عوض می‌شود؛ بقیهٔ کلیدها (مثل code) می‌مانند
        body = dict(response.data) if isinstance(response.data, dict) else {}
        body["detail"] = message
        body["message"] = message
        response.data = body
    else:
        response.data = _with_message(response.data, message)
    return response
