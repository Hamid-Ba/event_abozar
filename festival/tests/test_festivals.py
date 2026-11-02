"""
Multi-festival, single registration + many works, multi-file upload, Persian errors
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from festival.models import (
    Festival,
    FestivalFormat,
    FestivalRegistration,
    FestivalTopic,
    Work,
    WorkFile,
)
from festival.tests.utils import make_festival
from province.models import City, Province

User = get_user_model()


def pdf(name="a.pdf", size=100):
    return SimpleUploadedFile(name, b"x" * size, content_type="application/pdf")


def mp4(name="v.mp4", size=100):
    return SimpleUploadedFile(name, b"x" * size, content_type="video/mp4")


class FestivalBase(APITestCase):
    def setUp(self):
        self.province = Province.objects.create(name="تهران", slug="tehran")
        self.city = City.objects.create(
            name="تهران", slug="tehran-city", province=self.province
        )
        self.user = User.objects.create(phone="09120000001", fullName="کاربر")
        self.other_user = User.objects.create(phone="09120000002", fullName="دیگری")
        self.format_video = FestivalFormat.objects.get(code="video_clip")
        self.format_podcast = FestivalFormat.objects.get(code="podcast")
        self.topic_a = FestivalTopic.objects.get(code="year_slogan")
        self.topic_b = FestivalTopic.objects.get(code="jihad_explanation")
        self.festival = make_festival()
        self.client.force_authenticate(user=self.user)

    def personal_data(self, **extra):
        data = {
            "full_name": "علی احمدی",
            "father_name": "محمد",
            "national_id": "1234567890",
            "gender": "male",
            "education": "کارشناسی",
            "phone_number": "09120000001",
            "province_id": self.province.id,
            "city_id": self.city.id,
            "media_name": "رسانه تست",
        }
        data.update(extra)
        return data

    def register(self, festival=None):
        festival = festival or self.festival
        return self.client.post(
            reverse("festival:festival-register", kwargs={"id": festival.id}),
            self.personal_data(),
            format="json",
        )


class FestivalListTest(FestivalBase):
    def test_default_lists_only_open_festivals(self):
        archived = make_festival(
            registration_start=timezone.now() - timedelta(days=60),
            registration_end=timezone.now() - timedelta(days=30),
        )
        upcoming = make_festival(
            registration_start=timezone.now() + timedelta(days=5),
            registration_end=timezone.now() + timedelta(days=35),
        )
        inactive = make_festival(is_active=False)
        second_open = make_festival()

        response = self.client.get(reverse("festival:festival-list"))
        ids = {f["id"] for f in response.data}
        self.assertEqual(ids, {self.festival.id, second_open.id})
        self.assertNotIn(archived.id, ids)
        self.assertNotIn(upcoming.id, ids)
        self.assertNotIn(inactive.id, ids)

    def test_archive_and_upcoming_filters(self):
        archived = make_festival(
            registration_start=timezone.now() - timedelta(days=60),
            registration_end=timezone.now() - timedelta(days=30),
        )
        upcoming = make_festival(
            registration_start=timezone.now() + timedelta(days=5),
            registration_end=timezone.now() + timedelta(days=35),
        )
        url = reverse("festival:festival-list")
        self.assertEqual(
            [f["id"] for f in self.client.get(url, {"status": "archived"}).data],
            [archived.id],
        )
        self.assertEqual(
            [f["id"] for f in self.client.get(url, {"status": "upcoming"}).data],
            [upcoming.id],
        )
        self.assertEqual(len(self.client.get(url, {"status": "all"}).data), 3)

    def test_featured_independent_of_other_festivals_and_ordered(self):
        featured_b = make_festival(is_featured=True, display_order=2)
        featured_a = make_festival(is_featured=True, display_order=1)
        make_festival(is_featured=False)
        # تیک خورده اما تمام‌شده: در صفحه اول نیست (آرشیو است)
        make_festival(
            is_featured=True,
            registration_start=timezone.now() - timedelta(days=60),
            registration_end=timezone.now() - timedelta(days=1),
        )
        # تیک خورده و هنوز شروع‌نشده: نمایش داده می‌شود
        upcoming_featured = make_festival(
            is_featured=True,
            display_order=3,
            registration_start=timezone.now() + timedelta(days=5),
            registration_end=timezone.now() + timedelta(days=35),
        )
        response = self.client.get(reverse("festival:festival-featured"))
        self.assertEqual(
            [f["id"] for f in response.data],
            [featured_a.id, featured_b.id, upcoming_featured.id],
        )

    def test_detail_shows_allowed_categories_and_upload_rules(self):
        self.festival.formats.add(self.format_video)
        response = self.client.get(
            reverse("festival:festival-detail", kwargs={"id": self.festival.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([f["code"] for f in response.data["formats"]], ["video_clip"])
        # topics خالی = همهٔ محورهای فعال
        self.assertGreater(len(response.data["topics"]), 1)
        self.assertIn("kinds", response.data["upload_rules"])
        self.assertIsNone(response.data["my_registration_id"])

    def test_inactive_festival_detail_is_404(self):
        festival = make_festival(is_active=False)
        response = self.client.get(
            reverse("festival:festival-detail", kwargs={"id": festival.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("message", response.data)

    def test_categories_filtered_by_festival(self):
        self.festival.formats.add(self.format_video)
        response = self.client.get(
            reverse("festival:format-list"), {"festival": self.festival.id}
        )
        self.assertEqual([f["code"] for f in response.data], ["video_clip"])
        response = self.client.get(reverse("festival:format-list"))
        self.assertGreater(len(response.data), 1)


class RegistrationTest(FestivalBase):
    def test_register_once_per_festival(self):
        first = self.register()
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.register()
        self.assertEqual(second.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(second.data["registration_id"], first.data["data"]["id"])
        self.assertIn("قبلاً", second.data["message"])
        self.assertEqual(
            FestivalRegistration.objects.filter(user=self.user).count(), 1
        )

    def test_same_user_can_register_in_two_festivals(self):
        other = make_festival()
        self.assertEqual(self.register().status_code, 201)
        self.assertEqual(self.register(other).status_code, 201)

    def test_register_closed_festival_rejected(self):
        closed = make_festival(
            registration_start=timezone.now() - timedelta(days=60),
            registration_end=timezone.now() - timedelta(days=1),
        )
        response = self.register(closed)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("مهلت", response.data["message"])

    def test_register_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.register()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("وارد", response.data["message"])

    def test_register_city_must_belong_to_province(self):
        other_province = Province.objects.create(name="اصفهان", slug="isfahan")
        other_city = City.objects.create(
            name="اصفهان", slug="isfahan-city", province=other_province
        )
        response = self.client.post(
            reverse("festival:festival-register", kwargs={"id": self.festival.id}),
            self.personal_data(city_id=other_city.id),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)

    def test_my_registration_id_in_detail(self):
        registration_id = self.register().data["data"]["id"]
        response = self.client.get(
            reverse("festival:festival-detail", kwargs={"id": self.festival.id})
        )
        self.assertEqual(response.data["my_registration_id"], registration_id)

    def test_update_personal_info_but_not_national_id(self):
        registration_id = self.register().data["data"]["id"]
        url = reverse(
            "festival:my-registration-detail", kwargs={"id": registration_id}
        )
        response = self.client.patch(
            url, {"media_name": "رسانهٔ جدید", "national_id": "0000000000"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["media_name"], "رسانهٔ جدید")
        self.assertEqual(response.data["national_id"], "1234567890")

    def test_cannot_update_other_users_registration(self):
        registration_id = self.register().data["data"]["id"]
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            reverse("festival:my-registration-detail", kwargs={"id": registration_id}),
            {"media_name": "x"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_legacy_endpoint_defaults_to_sole_open_festival(self):
        self.client.force_authenticate(user=None)
        data = self.personal_data()
        response = self.client.post(
            reverse("festival:registration-create"), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        registration = FestivalRegistration.objects.get(national_id="1234567890")
        self.assertEqual(registration.festival_id, self.festival.id)

    def test_legacy_endpoint_needs_festival_when_several_open(self):
        make_festival()
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse("festival:registration-create"), self.personal_data(), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("festival", response.data)

    def test_my_festivals_lists_all_registered_festivals(self):
        other = make_festival()
        reg1 = self.register().data["data"]["id"]
        self.register(other)
        self.client.post(
            reverse("festival:work-list"),
            {
                "festival_registration": reg1,
                "festival_format": "video_clip",
                "festival_topic": "year_slogan",
                "title": "اثر اول",
                "description": "توضیحات",
                "files": [mp4()],
            },
            format="multipart",
        )
        not_registered = make_festival()
        response = self.client.get(reverse("festival:my-festivals"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        by_festival = {item["festival"]["id"]: item for item in response.data}
        self.assertEqual(set(by_festival), {self.festival.id, other.id})
        self.assertNotIn(not_registered.id, by_festival)
        self.assertEqual(by_festival[self.festival.id]["works_count"], 1)
        self.assertEqual(by_festival[other.id]["works_count"], 0)


class WorkUploadTest(FestivalBase):
    def setUp(self):
        super().setUp()
        self.registration_id = self.register().data["data"]["id"]

    def work_data(self, **extra):
        data = {
            "festival_registration": self.registration_id,
            "festival_format": "video_clip",
            "festival_topic": "year_slogan",
            "title": "اثر نمونه",
            "description": "توضیحات",
        }
        data.update(extra)
        return data

    def post_work(self, **extra):
        return self.client.post(
            reverse("festival:work-list"), self.work_data(**extra), format="multipart"
        )

    def test_one_registration_many_works_with_different_formats_and_topics(self):
        video = self.post_work(
            files=[mp4("video.mp4"), mp4("podcast.mp4")],
            title="ویدیو و پادکست",
        )
        self.assertEqual(video.status_code, status.HTTP_201_CREATED, video.data)
        self.assertEqual(len(video.data["files"]), 2)
        self.assertEqual(video.data["status"], "submitted")

        article = self.post_work(
            festival_format="podcast",
            festival_topic="jihad_explanation",
            files=[pdf("article.pdf")],
            title="مقاله",
        )
        self.assertEqual(article.status_code, status.HTTP_201_CREATED, article.data)

        works = Work.objects.filter(festival_registration_id=self.registration_id)
        self.assertEqual(works.count(), 2)
        self.assertEqual(
            {w.festival_format.code for w in works}, {"video_clip", "podcast"}
        )
        self.assertEqual(
            FestivalRegistration.objects.filter(user=self.user).count(), 1
        )

    def test_work_without_files_is_draft_then_files_added(self):
        response = self.post_work()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "draft")
        work_id = response.data["id"]

        added = self.client.post(
            reverse("festival:work-files", kwargs={"pk": work_id}),
            {"files": [mp4(), pdf()]},
            format="multipart",
        )
        self.assertEqual(added.status_code, status.HTTP_201_CREATED, added.data)
        self.assertEqual(len(added.data), 2)
        self.assertEqual(Work.objects.get(pk=work_id).status, "submitted")

    def test_delete_last_file_returns_work_to_draft(self):
        work_id = self.post_work(files=[pdf()]).data["id"]
        file_id = WorkFile.objects.get(work_id=work_id).id
        response = self.client.delete(
            reverse(
                "festival:work-file-detail", kwargs={"pk": work_id, "file_id": file_id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Work.objects.get(pk=work_id).status, "draft")

    def test_format_and_topic_required_on_new_flow(self):
        data = self.work_data()
        del data["festival_format"]
        response = self.client.post(reverse("festival:work-list"), data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("festival_format", response.data)

    def test_format_must_be_allowed_in_festival(self):
        self.festival.formats.add(self.format_podcast)
        response = self.post_work(festival_format="video_clip")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("برگزار نمی‌شود", str(response.data["festival_format"][0]))

    def test_unknown_extension_has_persian_message(self):
        bad = SimpleUploadedFile("run.exe", b"x" * 10)
        response = self.post_work(files=[bad])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("فرمت فایل «run.exe» مجاز نیست", response.data["message"])
        self.assertFalse(Work.objects.exists())

    @override_settings(FESTIVAL_UPLOAD_LIMITS_MB={"video": 1})
    def test_oversize_file_message_has_name_size_and_limit(self):
        big = mp4("big.mp4", size=2 * 1024 * 1024 + 1)
        response = self.post_work(files=[big])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        message = response.data["message"]
        self.assertIn("big.mp4", message)
        self.assertIn("2.0 مگابایت", message)
        self.assertIn("حداکثر حجم مجاز برای ویدیو 1 مگابایت", message)
        self.assertFalse(Work.objects.exists())

    @override_settings(FESTIVAL_MAX_FILES_PER_WORK=2)
    def test_max_files_per_work(self):
        response = self.post_work(files=[pdf("1.pdf"), pdf("2.pdf"), pdf("3.pdf")])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("حداکثر 2 فایل", response.data["message"])

        work_id = self.post_work(files=[pdf("1.pdf"), pdf("2.pdf")]).data["id"]
        response = self.client.post(
            reverse("festival:work-files", kwargs={"pk": work_id}),
            {"files": [pdf("3.pdf")]},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_file_rejected(self):
        response = self.post_work(files=[SimpleUploadedFile("e.pdf", b"")])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("خالی", response.data["message"])

    def test_cannot_add_work_to_other_users_registration(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.post_work()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_add_files_to_other_users_work(self):
        work_id = self.post_work().data["id"]
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(
            reverse("festival:work-files", kwargs={"pk": work_id}),
            {"files": [pdf()]},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_closed_festival_blocks_new_works_edit_and_delete(self):
        work_id = self.post_work(files=[pdf()]).data["id"]
        Festival.objects.filter(pk=self.festival.pk).update(
            registration_end=timezone.now() - timedelta(minutes=1)
        )
        self.assertEqual(self.post_work().status_code, status.HTTP_403_FORBIDDEN)
        detail = reverse("festival:work-detail", kwargs={"pk": work_id})
        self.assertEqual(
            self.client.patch(detail, {"title": "عنوان جدید"}, format="multipart").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(self.client.delete(detail).status_code, status.HTTP_403_FORBIDDEN)

    def test_work_under_review_is_locked(self):
        work_id = self.post_work(files=[pdf()]).data["id"]
        Work.objects.filter(pk=work_id).update(status=Work.STATUS_UNDER_REVIEW)
        detail = reverse("festival:work-detail", kwargs={"pk": work_id})
        response = self.client.delete(detail)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("داوری", response.data["message"])

    def test_update_work_title_and_append_file(self):
        work_id = self.post_work(files=[pdf("1.pdf")]).data["id"]
        detail = reverse("festival:work-detail", kwargs={"pk": work_id})
        response = self.client.patch(
            detail, {"title": "عنوان جدید", "files": [pdf("2.pdf")]}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["title"], "عنوان جدید")
        self.assertEqual(len(response.data["files"]), 2)

    def test_my_works_in_festival(self):
        self.post_work(files=[pdf()])
        response = self.client.get(
            reverse("festival:festival-my-works", kwargs={"id": self.festival.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["festival"]["id"], self.festival.id)

    def test_upload_rules_endpoint(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("festival:upload-rules"))
        self.assertEqual(response.status_code, 200)
        kinds = {k["kind"]: k for k in response.data["kinds"]}
        self.assertEqual(kinds["video"]["max_size_mb"], 100)
        self.assertIn("pdf", kinds["document"]["extensions"])


class LegacyDataMigrationTest(FestivalBase):
    """Work قدیمی (فقط فیلد file) هنوز درست نمایش داده می‌شود"""

    def test_legacy_work_without_workfile_still_serializes(self):
        registration = FestivalRegistration.objects.create(
            user=self.user,
            full_name="x",
            father_name="y",
            national_id="1234567890",
            gender="male",
            education="z",
            phone_number="09120000001",
            province=self.province,
            city=self.city,
            media_name="m",
            festival_format=self.format_video,
            festival_topic=self.topic_a,
        )
        work = Work.objects.create(
            festival_registration=registration,
            title="قدیمی",
            description="d",
            file=pdf("legacy.pdf"),
        )
        response = self.client.get(
            reverse("festival:work-detail", kwargs={"pk": work.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["file_url"].endswith(".pdf"))
        self.assertEqual(response.data["files"], [])
