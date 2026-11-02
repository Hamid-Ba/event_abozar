from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from festival.judging import submit_review
from festival.models import (
    FestivalFormat,
    FestivalRegistration,
    FestivalTopic,
    JudgeProfile,
    Notification,
    Review,
    Work,
    WorkFile,
)
from festival.tests.utils import make_festival
from formbuilder.models import Form, Question, Submission
from formbuilder.tasks import notify_opened_forms
from province.models import City, Province

User = get_user_model()


class Base(APITestCase):
    def setUp(self):
        province = Province.objects.create(name="تهران", slug="tehran")
        city = City.objects.create(name="تهران", slug="tehran-city", province=province)
        self.festival = make_festival(required_judges=2)
        self.participant = User.objects.create(phone="09120000001", fullName="شرکت‌کننده")
        self.outsider = User.objects.create(phone="09120000009", fullName="غریبه")
        self.registration = FestivalRegistration.objects.create(
            user=self.participant,
            festival=self.festival,
            full_name="علی احمدی",
            father_name="م",
            national_id="1234567890",
            gender="male",
            education="ک",
            phone_number="09120000001",
            province=province,
            city=city,
            media_name="رسانه",
        )
        self.judge = User.objects.create(phone="09130000001", fullName="داور ۱")
        JudgeProfile.objects.create(user=self.judge).festivals.add(self.festival)
        self.judge2 = User.objects.create(phone="09130000002", fullName="داور ۲")
        JudgeProfile.objects.create(user=self.judge2).festivals.add(self.festival)
        self.admin = User.objects.create(phone="09999999999", is_staff=True)

    def make_survey(self, **extra):
        data = {
            "festival": self.festival,
            "title": "نظرسنجی پایان جشنواره",
            "kind": Form.KIND_SURVEY,
            "audience": Form.AUDIENCE_PARTICIPANT,
        }
        data.update(extra)
        form = Form.objects.create(**data)
        self.q_rating = Question.objects.create(
            form=form, text="رضایت کلی", qtype="rating", min_value=1, max_value=5, order=1
        )
        self.q_choice = Question.objects.create(
            form=form, text="منبع آشنایی", qtype="single_choice", choices=["اینستاگرام", "دوستان"], order=2
        )
        self.q_multi = Question.objects.create(
            form=form, text="بخش‌های مفید", qtype="multi_choice", choices=["الف", "ب", "ج"], order=3, required=False
        )
        self.q_text = Question.objects.create(
            form=form, text="پیشنهاد", qtype="long_text", order=4, required=False
        )
        return form

    def submit(self, form, user, answers):
        self.client.force_authenticate(user=user)
        return self.client.post(
            reverse("formbuilder:form-submit", kwargs={"pk": form.pk}),
            {"answers": answers},
            format="json",
        )


class AudienceTest(Base):
    def test_participant_sees_only_participant_forms(self):
        survey = self.make_survey()
        judge_only = self.make_survey(audience=Form.AUDIENCE_JUDGE, title="ویژه داوران")
        both = self.make_survey(audience=Form.AUDIENCE_BOTH, title="هر دو")

        self.client.force_authenticate(user=self.participant)
        ids = {f["id"] for f in self.client.get(reverse("formbuilder:form-list")).data}
        self.assertEqual(ids, {survey.id, both.id})

        self.client.force_authenticate(user=self.judge)
        ids = {f["id"] for f in self.client.get(reverse("formbuilder:form-list")).data}
        self.assertEqual(ids, {judge_only.id, both.id})

    def test_outsider_sees_nothing_and_cannot_open_or_submit(self):
        survey = self.make_survey()
        self.client.force_authenticate(user=self.outsider)
        self.assertEqual(self.client.get(reverse("formbuilder:form-list")).data, [])
        self.assertEqual(
            self.client.get(reverse("formbuilder:form-detail", kwargs={"pk": survey.pk})).status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.submit(survey, self.outsider, {}).status_code, status.HTTP_404_NOT_FOUND
        )

    def test_closed_or_future_forms_not_listed_and_not_submittable(self):
        future = self.make_survey(opens_at=timezone.now() + timedelta(days=1))
        past = self.make_survey(closes_at=timezone.now() - timedelta(days=1))
        self.client.force_authenticate(user=self.participant)
        self.assertEqual(self.client.get(reverse("formbuilder:form-list")).data, [])
        response = self.submit(past, self.participant, {str(past.questions.first().id): 3})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("زمان پاسخ‌دهی", response.data["message"])
        self.assertEqual(
            self.submit(future, self.participant, {}).status_code, status.HTTP_403_FORBIDDEN
        )

    def test_festival_scoped_form_requires_registration_in_that_festival(self):
        other = make_festival()
        form = self.make_survey(festival=other)
        self.client.force_authenticate(user=self.participant)
        self.assertEqual(self.client.get(reverse("formbuilder:form-list")).data, [])
        self.assertEqual(self.submit(form, self.participant, {}).status_code, 404)

    def test_detail_includes_questions_in_order(self):
        survey = self.make_survey()
        self.client.force_authenticate(user=self.participant)
        response = self.client.get(reverse("formbuilder:form-detail", kwargs={"pk": survey.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [q["qtype"] for q in response.data["questions"]],
            ["rating", "single_choice", "multi_choice", "long_text"],
        )


class SubmitTest(Base):
    def valid_answers(self, survey):
        return {
            str(self.q_rating.id): 4,
            str(self.q_choice.id): "دوستان",
            str(self.q_multi.id): ["الف", "ج"],
            str(self.q_text.id): "عالی بود",
        }

    def test_submit_success_and_only_once(self):
        survey = self.make_survey()
        response = self.submit(survey, self.participant, self.valid_answers(survey))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        submission = Submission.objects.get(form=survey, user=self.participant)
        self.assertEqual(submission.registration_id, self.registration.id)
        self.assertEqual(submission.answers.count(), 4)

        again = self.submit(survey, self.participant, self.valid_answers(survey))
        self.assertEqual(again.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("قبلاً", again.data["message"])

        self.client.force_authenticate(user=self.participant)
        listed = self.client.get(reverse("formbuilder:form-list")).data
        self.assertTrue(listed[0]["submitted"])

    def test_required_questions(self):
        survey = self.make_survey()
        response = self.submit(survey, self.participant, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("رضایت کلی", response.data["message"])
        self.assertIn(str(self.q_rating.id), response.data["answers"])
        self.assertFalse(Submission.objects.exists())

    def test_rating_range_and_type(self):
        survey = self.make_survey()
        answers = self.valid_answers(survey)
        for bad in (6, 0, "abc", True, None):
            answers[str(self.q_rating.id)] = bad
            response = self.submit(survey, self.participant, answers)
            self.assertEqual(response.status_code, 400, bad)
        answers[str(self.q_rating.id)] = "5"
        self.assertEqual(self.submit(survey, self.participant, answers).status_code, 201)

    def test_choice_validation(self):
        survey = self.make_survey()
        answers = self.valid_answers(survey)
        answers[str(self.q_choice.id)] = "نامعتبر"
        self.assertEqual(self.submit(survey, self.participant, answers).status_code, 400)
        answers[str(self.q_choice.id)] = "دوستان"
        answers[str(self.q_multi.id)] = ["الف", "الف"]
        self.assertEqual(self.submit(survey, self.participant, answers).status_code, 400)
        answers[str(self.q_multi.id)] = ["د"]
        self.assertEqual(self.submit(survey, self.participant, answers).status_code, 400)

    def test_unknown_question_rejected(self):
        survey = self.make_survey()
        answers = self.valid_answers(survey)
        answers["99999"] = "x"
        self.assertEqual(self.submit(survey, self.participant, answers).status_code, 400)

    def test_file_question(self):
        survey = self.make_survey()
        q_file = Question.objects.create(form=survey, text="تصویر", qtype="file", required=True, order=5)
        self.client.force_authenticate(user=self.participant)
        url = reverse("formbuilder:form-submit", kwargs={"pk": survey.pk})
        import json

        payload = {
            "answers": json.dumps(self.valid_answers(survey)),
            f"file_{q_file.id}": SimpleUploadedFile("run.exe", b"x" * 10),
        }
        response = self.client.post(url, payload, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertIn("مجاز نیست", response.data["message"])

        payload[f"file_{q_file.id}"] = SimpleUploadedFile("p.pdf", b"x" * 10)
        response = self.client.post(url, payload, format="multipart")
        self.assertEqual(response.status_code, 201, response.data)

    def test_judge_and_participant_can_both_answer_a_both_form(self):
        survey = self.make_survey(audience=Form.AUDIENCE_BOTH)
        answers = self.valid_answers(survey)
        self.assertEqual(self.submit(survey, self.participant, answers).status_code, 201)
        self.assertEqual(self.submit(survey, self.judge, answers).status_code, 201)


class AdminReportTest(Base):
    def test_admin_results_split_by_role_and_anonymity(self):
        survey = self.make_survey(audience=Form.AUDIENCE_BOTH, is_anonymous=True)
        answers = {str(self.q_rating.id): 4, str(self.q_choice.id): "دوستان"}
        Base.submit(self, survey, self.participant, answers)
        answers[str(self.q_rating.id)] = 2
        Base.submit(self, survey, self.judge, answers)

        self.client.force_authenticate(user=self.admin)
        url = reverse("formbuilder:admin-submissions", kwargs={"pk": survey.pk})
        everyone = self.client.get(url)
        self.assertEqual(len(everyone.data), 2)
        self.assertTrue(all(s["user"] is None and s["user_name"] is None for s in everyone.data))
        judges = self.client.get(url, {"role": "judge"})
        self.assertEqual([s["role"] for s in judges.data], ["judge"])

        summary = self.client.get(reverse("formbuilder:admin-summary", kwargs={"pk": survey.pk}))
        rating = next(q for q in summary.data["questions"] if q["qtype"] == "rating")
        self.assertEqual(rating["average"], 3.0)
        choice = next(q for q in summary.data["questions"] if q["qtype"] == "single_choice")
        self.assertEqual(choice["choices"], {"اینستاگرام": 0, "دوستان": 2})

        csv = self.client.get(reverse("formbuilder:admin-export", kwargs={"pk": survey.pk}))
        self.assertEqual(csv.status_code, 200)
        body = csv.content.decode("utf-8-sig")
        self.assertIn("رضایت کلی", body)
        self.assertNotIn("09120000001", body)  # ناشناس

    def test_admin_endpoints_forbidden_for_non_staff(self):
        survey = self.make_survey()
        for user in (self.participant, self.judge):
            self.client.force_authenticate(user=user)
            for name in ("admin-submissions", "admin-summary", "admin-export"):
                response = self.client.get(reverse(f"formbuilder:{name}", kwargs={"pk": survey.pk}))
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class JudgingFormTest(Base):
    def setUp(self):
        super().setUp()
        self.work = Work.objects.create(
            festival_registration=self.registration,
            festival_format=FestivalFormat.objects.get(code="video_clip"),
            festival_topic=FestivalTopic.objects.get(code="year_slogan"),
            title="اثر",
            description="d",
            status=Work.STATUS_SUBMITTED,
        )
        WorkFile.objects.create(
            work=self.work, file=SimpleUploadedFile("a.pdf", b"x"), original_name="a.pdf", kind="document", size=1
        )
        self.form = Form.objects.create(festival=self.festival, title="فرم داوری", kind=Form.KIND_JUDGING)
        self.c1 = Question.objects.create(form=self.form, text="خلاقیت", qtype="rating", min_value=0, max_value=10, order=1)
        self.c2 = Question.objects.create(form=self.form, text="کیفیت فنی", qtype="rating", min_value=0, max_value=20, order=2)
        self.c3 = Question.objects.create(form=self.form, text="توضیح", qtype="long_text", required=False, order=3)

    def post(self, judge, answers, **extra):
        self.client.force_authenticate(user=judge)
        return self.client.post(
            reverse("formbuilder:judging-review", kwargs={"pk": self.work.pk}),
            {"answers": answers, **extra},
            format="json",
        )

    def test_judging_form_forces_audience_and_is_hidden_from_survey_list(self):
        self.assertEqual(self.form.audience, Form.AUDIENCE_JUDGE)
        self.client.force_authenticate(user=self.judge)
        self.assertEqual(self.client.get(reverse("formbuilder:form-list")).data, [])

    def test_judge_score_is_sum_of_criteria_and_final_is_sum_of_judges(self):
        r1 = self.post(self.judge, {str(self.c1.id): 7, str(self.c2.id): 15, str(self.c3.id): "خوب"})
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED, r1.data)
        r2 = self.post(self.judge2, {str(self.c1.id): 5, str(self.c2.id): 10})
        self.assertEqual(r2.status_code, 201, r2.data)

        scores = sorted(Review.objects.values_list("score", flat=True))
        self.assertEqual(scores, [Decimal("15.00"), Decimal("22.00")])
        self.work.refresh_from_db()
        self.assertEqual(self.work.final_score, Decimal("37.00"))
        self.assertEqual(self.work.status, Work.STATUS_JUDGED)
        self.assertEqual(Submission.objects.filter(form=self.form, work=self.work).count(), 2)

    def test_criteria_ranges_and_required(self):
        self.assertEqual(self.post(self.judge, {str(self.c1.id): 11, str(self.c2.id): 1}).status_code, 400)
        self.assertEqual(self.post(self.judge, {str(self.c1.id): 3}).status_code, 400)  # c2 الزامی
        self.assertFalse(Review.objects.exists())
        self.assertFalse(Submission.objects.exists())

    def test_second_review_by_same_judge_is_rejected_and_rolled_back(self):
        answers = {str(self.c1.id): 1, str(self.c2.id): 1}
        self.assertEqual(self.post(self.judge, answers).status_code, 201)
        response = self.post(self.judge, answers)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Submission.objects.filter(user=self.judge).count(), 1)

    def test_plain_score_endpoint_blocked_when_form_exists(self):
        self.client.force_authenticate(user=self.judge)
        response = self.client.post(
            reverse("festival:judge-review-create", kwargs={"pk": self.work.pk}),
            {"score": 50},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("فرم داوری", response.data["message"])

    def test_judge_work_exposes_form_id(self):
        self.client.force_authenticate(user=self.judge)
        response = self.client.get(reverse("festival:judge-works"))
        self.assertEqual(response.data[0]["judging_form"], self.form.id)

    def test_only_one_active_judging_form_per_festival(self):
        from django.core.exceptions import ValidationError

        duplicate = Form(festival=self.festival, title="دومی", kind=Form.KIND_JUDGING)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()


class NotificationTest(Base):
    def test_form_opened_notification_sent_once_to_audience_only(self):
        survey = self.make_survey(audience=Form.AUDIENCE_PARTICIPANT)
        sent = notify_opened_forms()
        self.assertEqual(sent, 1)
        self.assertEqual(Notification.objects.filter(user=self.participant, kind="form_opened").count(), 1)
        self.assertFalse(Notification.objects.filter(user=self.judge).exists())
        self.assertFalse(Notification.objects.filter(user=self.outsider).exists())
        self.assertEqual(notify_opened_forms(), 0)  # فقط یک‌بار
        survey.refresh_from_db()
        self.assertIsNotNone(survey.notified_at)

    def test_future_form_not_notified_until_open(self):
        self.make_survey(opens_at=timezone.now() + timedelta(days=1))
        self.assertEqual(notify_opened_forms(), 0)

    def test_work_status_change_notifies_author_without_score(self):
        work = Work.objects.create(
            festival_registration=self.registration,
            festival_format=FestivalFormat.objects.get(code="video_clip"),
            festival_topic=FestivalTopic.objects.get(code="year_slogan"),
            title="اثر من",
            description="d",
            status=Work.STATUS_SUBMITTED,
        )
        WorkFile.objects.create(
            work=work, file=SimpleUploadedFile("a.pdf", b"x"), original_name="a.pdf", kind="document", size=1
        )
        submit_review(judge=self.judge, work_id=work.pk, score=88)
        submit_review(judge=self.judge2, work_id=work.pk, score=77)
        titles = list(
            Notification.objects.filter(user=self.participant).order_by("id").values_list("title", flat=True)
        )
        self.assertEqual(titles, ["اثر شما وارد مرحله داوری شد", "داوری اثر شما به پایان رسید"])
        for notification in Notification.objects.filter(user=self.participant):
            self.assertNotIn("88", notification.body)
            self.assertNotIn("165", notification.body)

    def test_notification_endpoints(self):
        Notification.objects.create(user=self.participant, kind="work_status", title="a")
        Notification.objects.create(user=self.participant, kind="work_status", title="b")
        Notification.objects.create(user=self.judge, kind="work_status", title="c")
        self.client.force_authenticate(user=self.participant)
        self.assertEqual(len(self.client.get(reverse("festival:notifications")).data), 2)
        self.assertEqual(self.client.get(reverse("festival:notifications-unread-count")).data["unread"], 2)
        first = Notification.objects.filter(user=self.participant).first()
        self.client.post(reverse("festival:notification-read", kwargs={"pk": first.pk}))
        self.assertEqual(self.client.get(reverse("festival:notifications-unread-count")).data["unread"], 1)
        self.client.post(reverse("festival:notifications-read-all"))
        self.assertEqual(self.client.get(reverse("festival:notifications-unread-count")).data["unread"], 0)
        # اعلان دیگران دست‌نخورده
        self.assertFalse(Notification.objects.get(user=self.judge).is_read)
