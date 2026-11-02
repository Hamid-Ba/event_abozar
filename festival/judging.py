"""
Judging services
قواعد داوری:
- داور فقط آثار جشنواره‌هایی را می‌بیند که به او داده شده، و فقط آثاری که خودش امتیاز نداده و داوری‌شان کامل نشده.
- هر داور به هر اثر یک‌بار امتیاز می‌دهد (۰ تا سقف جشنواره). امتیاز نهایی اثر = مجموع امتیازها.
- وقتی تعداد امتیازها به `required_judges` برسد اثر «داوری‌شده» می‌شود و از دید داوران حذف می‌شود.
"""
from decimal import Decimal

from django.db import transaction
from django.db.models import Exists, F, OuterRef
from rest_framework import permissions, status
from rest_framework.exceptions import APIException

from festival.models import Review, Work, WorkFile


class IsJudge(permissions.BasePermission):
    message = "این بخش فقط برای داوران است."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        profile = getattr(user, "judge_profile", None)
        return bool(profile and profile.is_active)


class WorkNotReviewable(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "این اثر در حال حاضر قابل داوری نیست."
    default_code = "work_not_reviewable"


class AlreadyReviewed(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "شما قبلاً به این اثر امتیاز داده‌اید."
    default_code = "already_reviewed"


class JudgingComplete(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "داوری این اثر با امتیاز سایر داوران کامل شد و دیگر امتیازی ثبت نمی‌شود."
    default_code = "judging_complete"


def reviewable_works(judge):
    """آثاری که این داور هنوز می‌تواند داوری کند"""
    profile = judge.judge_profile
    return (
        Work.objects.filter(
            festival_registration__festival__in=profile.festivals.all(),
            status__in=[Work.STATUS_SUBMITTED, Work.STATUS_UNDER_REVIEW],
            reviews_count__lt=F("festival_registration__festival__required_judges"),
        )
        .filter(Exists(WorkFile.objects.filter(work=OuterRef("pk"))))
        .exclude(reviews__judge=judge)
    )


def assigned_works(judge):
    """همهٔ آثار جشنواره‌های این داور (برای دیدن جزئیات اثری که قبلاً داوری کرده)"""
    return Work.objects.filter(
        festival_registration__festival__in=judge.judge_profile.festivals.all(),
        status__in=[Work.STATUS_SUBMITTED, Work.STATUS_UNDER_REVIEW, Work.STATUS_JUDGED],
    )


@transaction.atomic
def submit_review(*, judge, work_id, score, note=""):
    """
    ثبت امتیاز یک داور. ردیف اثر قفل می‌شود تا دو داور هم‌زمان نتوانند از سقف تعداد داوران عبور کنند.
    """
    allowed = assigned_works(judge).filter(pk=work_id).values_list("pk", flat=True)
    if not allowed:
        raise WorkNotReviewable("اثر پیدا نشد یا اجازهٔ داوری آن را ندارید.")

    # قفل ردیف اثر (در SQLite نادیده گرفته می‌شود؛ در PostgreSQL ردیف را تا پایان تراکنش قفل می‌کند)
    work = Work.objects.select_for_update().get(pk=work_id)
    festival = work.festival_registration.festival

    if work.status not in (Work.STATUS_SUBMITTED, Work.STATUS_UNDER_REVIEW):
        raise JudgingComplete() if work.status == Work.STATUS_JUDGED else WorkNotReviewable()
    if Review.objects.filter(work=work, judge=judge).exists():
        raise AlreadyReviewed()
    if work.reviews.count() >= festival.required_judges:
        raise JudgingComplete()

    score = Decimal(str(score))
    review = Review.objects.create(work=work, judge=judge, score=score, note=note or "")
    # signal امتیاز نهایی و وضعیت را به‌روز کرده؛ نسخهٔ تازه را برمی‌گردانیم
    review.work.refresh_from_db()
    return review
