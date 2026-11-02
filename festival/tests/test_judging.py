"""
Judging: هر داور امتیاز می‌دهد، امتیاز نهایی = مجموع امتیازها، سقف تعداد داور، دید داورها
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from festival.judging import submit_review
from festival.models import (
    FestivalFormat,
    FestivalRegistration,
    FestivalTopic,
    JudgeProfile,
    Review,
    Work,
    WorkFile,
)
from festival.tests.utils import make_festival
from province.models import City, Province

User = get_user_model()


class JudgingBase(APITestCase):
    def setUp(self):
        self.province = Province.objects.create(name="تهران", slug="tehran")
        self.city = City.objects.create(
            name="تهران", slug="tehran-city", province=self.province
        )
        self.festival = make_festival(required_judges=3, max_score=100)
        self.author = User.objects.create(phone="09120000001", fullName="سازنده")
        self.registration = FestivalRegistration.objects.create(
            user=self.author,
            festival=self.festival,
            full_name="علی احمدی",
            father_name="محمد",
            national_id="1234567890",
            gender="male",
            education="کارشناسی",
            phone_number="09120000001",
            province=self.province,
            city=self.city,
            media_name="رسانه",
        )
        self.work = self.make_work("اثر اول")
        self.judges = [self.make_judge(f"0913000000{i}") for i in range(1, 6)]
        self.admin = User.objects.create(phone="09999999999", is_staff=True)

    def make_work(self, title, with_file=True, festival_registration=None):
        work = Work.objects.create(
            festival_registration=festival_registration or self.registration,
            festival_format=FestivalFormat.objects.get(code="video_clip"),
            festival_topic=FestivalTopic.objects.get(code="year_slogan"),
            title=title,
            description="d",
            status=Work.STATUS_SUBMITTED if with_file else Work.STATUS_DRAFT,
        )
        if with_file:
            WorkFile.objects.create(
                work=work,
                file=SimpleUploadedFile("a.pdf", b"x"),
                original_name="a.pdf",
                kind="document",
                size=1,
            )
        return work

    def make_judge(self, phone, festivals=None):
        user = User.objects.create(phone=phone, fullName=f"داور {phone}")
        profile = JudgeProfile.objects.create(user=user)
        profile.festivals.set(festivals if festivals is not None else [self.festival])
        return user

    def review(self, judge, work, score, note=""):
        self.client.force_authenticate(user=judge)
        return self.client.post(
            reverse("festival:judge-review-create", kwargs={"pk": work.pk}),
            {"score": score, "note": note},
            format="json",
        )


class ScoreSumTest(JudgingBase):
    def test_final_score_is_sum_of_all_judges_scores(self):
        for judge, score in zip(self.judges[:3], ["80", "70.5", "90"]):
            response = self.review(judge, self.work, score)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.work.refresh_from_db()
        self.assertEqual(self.work.final_score, Decimal("240.50"))
        self.assertEqual(self.work.reviews_count, 3)
        self.assertEqual(self.work.status, Work.STATUS_JUDGED)

    def test_status_under_review_until_quorum(self):
        self.review(self.judges[0], self.work, 50)
        self.work.refresh_from_db()
        self.assertEqual(self.work.status, Work.STATUS_UNDER_REVIEW)
        self.assertEqual(self.work.final_score, Decimal("50.00"))
        self.review(self.judges[1], self.work, 60)
        self.work.refresh_from_db()
        self.assertEqual(self.work.status, Work.STATUS_UNDER_REVIEW)
        self.assertEqual(self.work.final_score, Decimal("110.00"))

    def test_fourth_judge_cannot_add_score_after_quorum(self):
        for judge in self.judges[:3]:
            self.review(judge, self.work, 10)
        response = self.review(self.judges[3], self.work, 99)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Review.objects.filter(work=self.work).count(), 3)
        self.work.refresh_from_db()
        self.assertEqual(self.work.final_score, Decimal("30.00"))

    def test_service_refuses_over_quorum(self):
        for judge in self.judges[:3]:
            submit_review(judge=judge, work_id=self.work.pk, score=5)
        with self.assertRaises(Exception):
            submit_review(judge=self.judges[3], work_id=self.work.pk, score=5)
        self.assertEqual(Review.objects.filter(work=self.work).count(), 3)

    def test_judge_cannot_score_twice(self):
        self.assertEqual(self.review(self.judges[0], self.work, 50).status_code, 201)
        response = self.review(self.judges[0], self.work, 60)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("قبلاً", response.data["message"])
        self.work.refresh_from_db()
        self.assertEqual(self.work.final_score, Decimal("50.00"))

    def test_score_range(self):
        response = self.review(self.judges[0], self.work, 101)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("حداکثر 100", response.data["message"])
        self.assertEqual(self.review(self.judges[0], self.work, -1).status_code, 400)
        self.assertEqual(self.review(self.judges[0], self.work, "abc").status_code, 400)
        self.assertEqual(self.review(self.judges[0], self.work, 0).status_code, 201)

    def test_deleting_a_review_recalculates(self):
        self.review(self.judges[0], self.work, 40)
        self.review(self.judges[1], self.work, 60)
        Review.objects.filter(judge=self.judges[1]).first().delete()
        self.work.refresh_from_db()
        self.assertEqual(self.work.final_score, Decimal("40.00"))
        self.assertEqual(self.work.reviews_count, 1)
        Review.objects.all().delete()
        self.work.refresh_from_db()
        self.assertIsNone(self.work.final_score)
        self.assertEqual(self.work.status, Work.STATUS_SUBMITTED)


class JudgeVisibilityTest(JudgingBase):
    def listed_ids(self, judge, **params):
        self.client.force_authenticate(user=judge)
        response = self.client.get(reverse("festival:judge-works"), params)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        return [w["id"] for w in response.data]

    def test_judge_sees_only_unreviewed_and_incomplete_works(self):
        done = self.make_work("کامل‌شده")
        mine = self.make_work("امتیازداده")
        for judge in self.judges[:3]:
            submit_review(judge=judge, work_id=done.pk, score=1)
        submit_review(judge=self.judges[4], work_id=mine.pk, score=1)

        self.assertEqual(
            set(self.listed_ids(self.judges[4])), {self.work.pk}
        )  # done کامل است، mine را خودش امتیاز داده
        self.assertEqual(
            set(self.listed_ids(self.judges[3])), {self.work.pk, mine.pk}
        )  # done کامل است

    def test_draft_work_is_not_listed(self):
        draft = self.make_work("پیش‌نویس", with_file=False)
        self.assertNotIn(draft.pk, self.listed_ids(self.judges[0]))

    def test_judge_does_not_see_other_festivals(self):
        other_festival = make_festival()
        outsider = self.make_judge("09140000001", festivals=[other_festival])
        self.assertEqual(self.listed_ids(outsider), [])
        self.client.force_authenticate(user=outsider)
        response = self.client.get(
            reverse("festival:judge-work-detail", kwargs={"pk": self.work.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.review(outsider, self.work, 5).status_code, 409)

    def test_non_judge_forbidden(self):
        self.client.force_authenticate(user=self.author)
        response = self.client.get(reverse("festival:judge-works"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_judge_forbidden(self):
        JudgeProfile.objects.filter(user=self.judges[0]).update(is_active=False)
        judge = type(self.judges[0]).objects.get(pk=self.judges[0].pk)
        self.client.force_authenticate(user=judge)
        response = self.client.get(reverse("festival:judge-works"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_judge_view_hides_author_identity(self):
        self.client.force_authenticate(user=self.judges[0])
        response = self.client.get(reverse("festival:judge-works"))
        body = str(response.data)
        self.assertNotIn("علی احمدی", body)
        self.assertNotIn("09120000001", body)
        self.assertNotIn("1234567890", body)

    def test_ordering(self):
        second = self.make_work("ب")
        ids = self.listed_ids(self.judges[0], ordering="-created_at")
        self.assertEqual(ids, [second.pk, self.work.pk])
        ids = self.listed_ids(self.judges[0], ordering="created_at")
        self.assertEqual(ids, [self.work.pk, second.pk])

    def test_my_reviews(self):
        self.review(self.judges[0], self.work, 77, note="خوب بود")
        response = self.client.get(reverse("festival:judge-my-reviews"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Decimal(response.data[0]["score"]), Decimal("77.00"))


class AdminJudgedWorksTest(JudgingBase):
    def test_admin_sees_judged_works_sorted_by_final_score(self):
        low = self.make_work("کم‌امتیاز")
        for judge in self.judges[:3]:
            submit_review(judge=judge, work_id=self.work.pk, score=90)
            submit_review(judge=judge, work_id=low.pk, score=10)
        incomplete = self.make_work("ناقص")
        submit_review(judge=self.judges[0], work_id=incomplete.pk, score=100)

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse("festival:admin-judged-works"))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual([w["id"] for w in response.data], [self.work.pk, low.pk])
        self.assertEqual(Decimal(response.data[0]["final_score"]), Decimal("270.00"))
        self.assertEqual(len(response.data[0]["reviews"]), 3)
        self.assertEqual(response.data[0]["author_name"], "علی احمدی")

        ascending = self.client.get(
            reverse("festival:admin-judged-works"), {"ordering": "final_score"}
        )
        self.assertEqual([w["id"] for w in ascending.data], [low.pk, self.work.pk])

    def test_judge_and_participant_cannot_use_admin_list(self):
        for user in (self.judges[0], self.author):
            self.client.force_authenticate(user=user)
            response = self.client.get(reverse("festival:admin-judged-works"))
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_participant_responses_do_not_expose_scores(self):
        for judge in self.judges[:3]:
            submit_review(judge=judge, work_id=self.work.pk, score=50)
        self.client.force_authenticate(user=self.author)
        detail = self.client.get(reverse("festival:work-detail", kwargs={"pk": self.work.pk}))
        self.assertNotIn("final_score", detail.data)
        self.assertNotIn("reviews", detail.data)
        listing = self.client.get(reverse("festival:work-list"))
        self.assertNotIn("final_score", listing.data[0])
