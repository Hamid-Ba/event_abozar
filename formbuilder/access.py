"""
Who can see / answer which form
"""
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

from festival.models import FestivalRegistration, JudgeProfile
from formbuilder.models import Form

User = get_user_model()


class UserRoles:
    """نقش‌های کاربر: شرکت‌کننده (ثبت‌نام در حداقل یک جشنواره) و/یا داور فعال"""

    def __init__(self, user):
        registrations = FestivalRegistration.objects.filter(user=user)
        self.registered_festival_ids = set(
            registrations.exclude(festival__isnull=True).values_list("festival_id", flat=True)
        )
        self.has_registration = registrations.exists()
        profile = JudgeProfile.objects.filter(user=user, is_active=True).first()
        self.is_judge = profile is not None
        self.judge_festival_ids = (
            set(profile.festivals.values_list("id", flat=True)) if profile else set()
        )

    def _participant_ok(self, form):
        if form.festival_id is None:
            return self.has_registration
        return form.festival_id in self.registered_festival_ids

    def _judge_ok(self, form):
        if not self.is_judge:
            return False
        return form.festival_id is None or form.festival_id in self.judge_festival_ids

    def can_access(self, form):
        if form.audience == Form.AUDIENCE_PARTICIPANT:
            return self._participant_ok(form)
        if form.audience == Form.AUDIENCE_JUDGE:
            return self._judge_ok(form)
        return self._participant_ok(form) or self._judge_ok(form)


def open_surveys():
    """نظرسنجی‌های فعالی که الان در بازهٔ زمانی خود باز هستند"""
    now = timezone.now()
    return (
        Form.objects.filter(is_active=True, kind=Form.KIND_SURVEY)
        .filter(Q(opens_at__isnull=True) | Q(opens_at__lte=now))
        .filter(Q(closes_at__isnull=True) | Q(closes_at__gte=now))
    )


def eligible_users(form):
    """کاربرانی که باید از باز شدن این فرم باخبر شوند"""
    user_ids = set()
    if form.audience in (Form.AUDIENCE_PARTICIPANT, Form.AUDIENCE_BOTH):
        registrations = FestivalRegistration.objects.all()
        if form.festival_id is not None:
            registrations = registrations.filter(festival_id=form.festival_id)
        user_ids |= set(registrations.values_list("user_id", flat=True))
    if form.audience in (Form.AUDIENCE_JUDGE, Form.AUDIENCE_BOTH):
        profiles = JudgeProfile.objects.filter(is_active=True)
        if form.festival_id is not None:
            profiles = profiles.filter(festivals=form.festival_id)
        user_ids |= set(profiles.values_list("user_id", flat=True))
    return User.objects.filter(pk__in=user_ids)
