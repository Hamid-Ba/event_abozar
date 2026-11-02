"""
Answer validation per question type
اعتبارسنجی پاسخ‌ها بر اساس نوع سؤال؛ همهٔ پیام‌ها فارسی و با نام سؤال
"""
from decimal import Decimal, InvalidOperation

from rest_framework import serializers

from festival.uploads import validate_upload
from formbuilder.models import Question

SHORT_TEXT_MAX = 500
LONG_TEXT_MAX = 5000


def _is_empty(value):
    return value is None or value == "" or value == []


def _to_number(value):
    if isinstance(value, bool):
        raise ValueError
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    if isinstance(value, str):
        return Decimal(value.strip())
    raise ValueError


def _clean_one(question, value, file):
    """مقدار تمیزشدهٔ یک سؤال؛ در خطا ValueError با پیام فارسی"""
    qtype = question.qtype

    if qtype == Question.TYPE_FILE:
        try:
            validate_upload(file)
        except ValueError as exc:
            raise ValueError(str(exc))
        return file.name[:255]

    if qtype in (Question.TYPE_SHORT_TEXT, Question.TYPE_LONG_TEXT):
        if not isinstance(value, str):
            raise ValueError("پاسخ باید متن باشد.")
        value = value.strip()
        limit = SHORT_TEXT_MAX if qtype == Question.TYPE_SHORT_TEXT else LONG_TEXT_MAX
        if len(value) > limit:
            raise ValueError(f"پاسخ نباید بیشتر از {limit} کاراکتر باشد.")
        return value

    if qtype == Question.TYPE_SINGLE_CHOICE:
        if not isinstance(value, str) or value not in question.choices:
            raise ValueError("گزینهٔ انتخاب‌شده معتبر نیست.")
        return value

    if qtype == Question.TYPE_MULTI_CHOICE:
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise ValueError("پاسخ باید فهرستی از گزینه‌ها باشد.")
        if len(set(value)) != len(value) or any(v not in question.choices for v in value):
            raise ValueError("گزینه‌های انتخاب‌شده معتبر نیستند.")
        return value

    if qtype == Question.TYPE_RATING:
        try:
            number = _to_number(value)
        except (ValueError, InvalidOperation):
            raise ValueError("امتیاز باید عدد باشد.")
        if not number.is_finite() or number < question.min_value or number > question.max_value:
            raise ValueError(
                f"امتیاز باید بین {question.min_value} و {question.max_value} باشد."
            )
        return int(number) if number == number.to_integral_value() else float(number)

    raise ValueError("نوع سؤال پشتیبانی نمی‌شود.")


def validate_answers(form, raw_answers, files=None):
    """
    raw_answers: {"<question_id>": value}   files: {"file_<question_id>": UploadedFile}
    خروجی: فهرست {question, value, file}. در خطا ValidationError با کلید answers برای هر سؤال.
    """
    files = files or {}
    if not isinstance(raw_answers, dict):
        raise serializers.ValidationError({"answers": ["قالب پاسخ‌ها معتبر نیست."]})

    questions = list(form.questions.all())
    known = {str(q.id) for q in questions}
    unknown = [key for key in raw_answers if str(key) not in known]
    if unknown:
        raise serializers.ValidationError(
            {"answers": ["پاسخ برای سؤالی ارسال شده که در این فرم وجود ندارد."]}
        )

    errors = {}
    cleaned = []
    for question in questions:
        file = files.get(f"file_{question.id}")
        value = raw_answers.get(str(question.id))
        provided = file is not None if question.qtype == Question.TYPE_FILE else not _is_empty(value)

        if not provided:
            if question.required:
                errors[str(question.id)] = [f"«{question.text}»: پاسخ این سؤال الزامی است."]
            continue
        try:
            clean = _clean_one(question, value, file)
        except ValueError as exc:
            errors[str(question.id)] = [f"«{question.text}»: {exc}"]
            continue
        cleaned.append(
            {
                "question": question,
                "value": clean,
                "file": file if question.qtype == Question.TYPE_FILE else None,
            }
        )

    if errors:
        raise serializers.ValidationError({"answers": errors})
    return cleaned
