"""
Form builder API
"""
import json
from collections import Counter

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, serializers, status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from festival.admin.exports import csv_response
from festival.judging import IsJudge, WorkNotReviewable, assigned_works, submit_review
from festival.models import FestivalRegistration
from formbuilder.access import UserRoles, open_surveys
from formbuilder.models import Answer, Form, Question, Submission
from formbuilder.serializers import (
    FormDetailSerializer,
    FormListSerializer,
    SubmissionReadSerializer,
)
from formbuilder.validation import validate_answers


class FormClosed(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "زمان پاسخ‌دهی به این فرم به پایان رسیده یا هنوز آغاز نشده است."
    default_code = "form_closed"


class AlreadySubmitted(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "شما قبلاً به این فرم پاسخ داده‌اید."
    default_code = "already_submitted"


def _parse_payload(request):
    """JSON: {"answers": {...}}   یا   multipart: answers=<json> و file_<id>=<فایل>"""
    data = request.data
    raw = data.get("answers", {})
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except ValueError:
            raise serializers.ValidationError({"answers": ["قالب پاسخ‌ها معتبر نیست."]})
    files = {key: value for key, value in request.FILES.items()}
    return raw, files


def _save_answers(submission, cleaned):
    Answer.objects.bulk_create(
        [
            Answer(
                submission=submission,
                question=item["question"],
                value=item["value"],
                file=item["file"],
            )
            for item in cleaned
        ]
    )


class FormListView(generics.ListAPIView):
    """نظرسنجی‌های بازِ مخصوص من (بر اساس نقش: شرکت‌کننده/داور)"""

    serializer_class = FormListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        roles = UserRoles(self.request.user)
        forms = open_surveys().select_related("festival")
        allowed_ids = [form.id for form in forms if roles.can_access(form)]
        return forms.filter(id__in=allowed_ids)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["submitted_form_ids"] = set(
            Submission.objects.filter(user=self.request.user, work__isnull=True).values_list(
                "form_id", flat=True
            )
        )
        return context

    @extend_schema(
        summary="نظرسنجی‌های من",
        description="فقط نظرسنجی‌های فعال و بازی که مخاطبشان من هستم. `submitted` نشان می‌دهد قبلاً پاسخ داده‌ام.",
        tags=["Forms"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FormDetailView(generics.RetrieveAPIView):
    serializer_class = FormDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        form = get_object_or_404(
            Form.objects.select_related("festival").prefetch_related("questions"),
            pk=self.kwargs["pk"],
            is_active=True,
            kind=Form.KIND_SURVEY,
        )
        if not UserRoles(self.request.user).can_access(form):
            raise NotFound()
        return form

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["submitted_form_ids"] = set(
            Submission.objects.filter(user=self.request.user, work__isnull=True).values_list(
                "form_id", flat=True
            )
        )
        return context

    @extend_schema(summary="فرم و سؤال‌ها", tags=["Forms"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FormSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @extend_schema(
        summary="ارسال پاسخ نظرسنجی",
        description=(
            "JSON: `{\"answers\": {\"<id سؤال>\": مقدار}}`. اگر سؤال فایلی دارد multipart بفرستید: "
            "`answers` (رشتهٔ JSON) و `file_<id سؤال>`. هر کاربر فقط یک‌بار می‌تواند پاسخ دهد."
        ),
        tags=["Forms"],
    )
    def post(self, request, pk):
        form = get_object_or_404(
            Form.objects.select_related("festival").prefetch_related("questions"),
            pk=pk,
            is_active=True,
            kind=Form.KIND_SURVEY,
        )
        if not UserRoles(request.user).can_access(form):
            raise NotFound()
        if not form.is_open:
            raise FormClosed()
        if Submission.objects.filter(form=form, user=request.user, work__isnull=True).exists():
            raise AlreadySubmitted()

        raw, files = _parse_payload(request)
        cleaned = validate_answers(form, raw, files)

        registration = None
        if form.festival_id:
            registration = FestivalRegistration.objects.filter(
                user=request.user, festival_id=form.festival_id
            ).first()
        try:
            with transaction.atomic():
                submission = Submission.objects.create(
                    form=form, user=request.user, registration=registration
                )
                _save_answers(submission, cleaned)
        except IntegrityError:
            raise AlreadySubmitted()
        return Response(
            {"message": "پاسخ شما ثبت شد. سپاس از همراهی شما.", "id": submission.id},
            status=status.HTTP_201_CREATED,
        )


class JudgingFormReviewView(APIView):
    """
    ثبت امتیاز داور با فرم داوری: معیارها همان سؤال‌های امتیازی فرم‌اند و
    امتیاز این داور برای اثر = مجموع امتیاز معیارها. (امتیاز نهایی اثر = مجموع امتیاز همهٔ داوران)
    """

    permission_classes = [IsJudge]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @extend_schema(
        summary="ثبت امتیاز با فرم داوری",
        description="`{\"answers\": {\"<id معیار>\": امتیاز}}`. امتیاز این داور = مجموع معیارهای امتیازی.",
        tags=["Forms"],
    )
    def post(self, request, pk):
        work = (
            assigned_works(request.user)
            .select_related("festival_registration__festival")
            .filter(pk=pk)
            .first()
        )
        if work is None:
            raise WorkNotReviewable("اثر پیدا نشد یا اجازهٔ داوری آن را ندارید.")

        form = (
            Form.objects.filter(
                festival=work.festival_registration.festival,
                kind=Form.KIND_JUDGING,
                is_active=True,
            )
            .prefetch_related("questions")
            .first()
        )
        if form is None:
            raise NotFound("برای این جشنواره فرم داوری تعریف نشده است.")
        if not form.is_open:
            raise FormClosed()

        raw, files = _parse_payload(request)
        cleaned = validate_answers(form, raw, files)
        rating_values = [
            item["value"] for item in cleaned if item["question"].qtype == Question.TYPE_RATING
        ]
        if not rating_values:
            raise serializers.ValidationError(
                {"answers": ["حداقل به یکی از معیارهای امتیازی فرم باید امتیاز بدهید."]}
            )
        score = sum(rating_values)
        note = request.data.get("note", "")
        note = note if isinstance(note, str) else ""

        with transaction.atomic():
            review = submit_review(
                judge=request.user, work_id=work.pk, score=score, note=note
            )
            submission = Submission.objects.create(form=form, user=request.user, work=work)
            _save_answers(submission, cleaned)
        return Response(
            {"id": review.id, "score": review.score, "submission": submission.id},
            status=status.HTTP_201_CREATED,
        )


# ------------------------------------------------------------------ admin side


def _admin_submissions(request, form):
    queryset = (
        Submission.objects.filter(form=form)
        .select_related("user", "user__judge_profile", "form", "work")
        .prefetch_related("answers__question")
    )
    role = request.query_params.get("role")
    if role == "judge":
        queryset = queryset.filter(user__judge_profile__isnull=False)
    elif role == "participant":
        queryset = queryset.filter(user__judge_profile__isnull=True)
    return queryset


class AdminSubmissionsView(generics.ListAPIView):
    serializer_class = SubmissionReadSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        form = get_object_or_404(Form, pk=self.kwargs["pk"])
        return _admin_submissions(self.request, form)

    @extend_schema(
        summary="پاسخ‌های یک فرم (مدیر)",
        description="`role=judge|participant` برای جداکردن پاسخ داوران و شرکت‌کنندگان. در فرم ناشناس هویت پاسخ‌دهنده نمایش داده نمی‌شود.",
        tags=["Forms"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdminSummaryView(APIView):
    """خلاصهٔ آماری: میانگین سؤال‌های امتیازی و تعداد هر گزینه"""

    permission_classes = [permissions.IsAdminUser]

    @extend_schema(summary="خلاصهٔ آماری پاسخ‌ها (مدیر)", tags=["Forms"])
    def get(self, request, pk):
        form = get_object_or_404(Form.objects.prefetch_related("questions"), pk=pk)
        submissions = _admin_submissions(request, form)
        answers = Answer.objects.filter(submission__in=submissions)
        by_question = {}
        for answer in answers:
            by_question.setdefault(answer.question_id, []).append(answer.value)

        result = []
        for question in form.questions.all():
            values = by_question.get(question.id, [])
            item = {
                "question": question.id,
                "text": question.text,
                "qtype": question.qtype,
                "count": len(values),
            }
            if question.qtype == Question.TYPE_RATING and values:
                item["average"] = round(sum(values) / len(values), 2)
                item["distribution"] = dict(Counter(str(v) for v in values))
            elif question.qtype in (Question.TYPE_SINGLE_CHOICE, Question.TYPE_MULTI_CHOICE):
                counter = Counter()
                for value in values:
                    counter.update(value if isinstance(value, list) else [value])
                item["choices"] = {choice: counter.get(choice, 0) for choice in question.choices}
            result.append(item)
        return Response(
            {"form": form.id, "title": form.title, "submissions": submissions.count(), "questions": result}
        )


class AdminExportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(summary="خروجی CSV پاسخ‌ها (مدیر)", tags=["Forms"])
    def get(self, request, pk):
        form = get_object_or_404(Form.objects.prefetch_related("questions"), pk=pk)
        return export_form_csv(form, _admin_submissions(request, form), request)


def export_form_csv(form, submissions, request=None):
    questions = list(form.questions.all())
    header = ["شناسه پاسخ", "پاسخ‌دهنده", "شماره تماس", "نقش", "اثر", "تاریخ"] + [
        q.text for q in questions
    ]
    rows = []
    for submission in submissions:
        by_question = {a.question_id: a for a in submission.answers.all()}
        row = [
            submission.id,
            "ناشناس" if form.is_anonymous else str(submission.user),
            "" if form.is_anonymous else submission.user.phone,
            "داور" if hasattr(submission.user, "judge_profile") else "شرکت‌کننده",
            submission.work.title if submission.work else "",
            submission.created_at.strftime("%Y-%m-%d %H:%M"),
        ]
        for question in questions:
            answer = by_question.get(question.id)
            if answer is None:
                row.append("")
            elif answer.file:
                url = answer.file.url
                row.append(request.build_absolute_uri(url) if request else url)
            elif isinstance(answer.value, list):
                row.append(" | ".join(answer.value))
            else:
                row.append("" if answer.value is None else answer.value)
        rows.append(row)
    return csv_response(f"form-{form.id}.csv", header, rows)
