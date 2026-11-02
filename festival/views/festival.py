"""
Festival Views
جشنواره‌ها: فهرست باز/آرشیو/صفحه اول، جزئیات، ثبت‌نام در جشنواره، «جشنواره‌های من»
"""
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from festival.models import Festival, FestivalRegistration, Work
from festival.serializers import (
    FestivalDetailSerializer,
    FestivalListSerializer,
    FestivalRegistrationSerializer,
    MyFestivalSerializer,
    MyRegistrationCreateSerializer,
    WorkListSerializer,
)
from festival.services import ensure_festival_open
from festival.uploads import upload_rules


class FestivalListView(generics.ListAPIView):
    """فهرست جشنواره‌ها؛ پیش‌فرض فقط جشنواره‌هایی که الان باز هستند"""

    serializer_class = FestivalListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        status_param = self.request.query_params.get("status", "open")
        queryset = Festival.objects.filter(is_active=True)
        if status_param == "open":
            queryset = Festival.objects.open()
        elif status_param == "upcoming":
            queryset = queryset.filter(registration_start__gt=timezone.now())
        elif status_param in ("archived", "archive", "closed"):
            queryset = Festival.objects.archived().filter(is_active=True)
        elif status_param != "all":
            queryset = Festival.objects.open()

        featured = self.request.query_params.get("featured")
        if featured and featured.lower() in ("1", "true", "yes"):
            queryset = queryset.filter(is_featured=True)
        return queryset.order_by("display_order", "-registration_start")

    @extend_schema(
        summary="فهرست جشنواره‌ها",
        description=(
            "به‌صورت پیش‌فرض فقط جشنواره‌هایی که ثبت‌نامشان الان باز است. "
            "با `status=archived` آرشیو، با `status=upcoming` جشنواره‌های آینده و با `status=all` همه."
        ),
        parameters=[
            OpenApiParameter(
                "status",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                enum=["open", "upcoming", "archived", "all"],
                required=False,
            ),
            OpenApiParameter("featured", OpenApiTypes.BOOL, OpenApiParameter.QUERY, required=False),
        ],
        tags=["Festivals"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FeaturedFestivalListView(generics.ListAPIView):
    """جشنواره‌هایی که مدیر برای صفحهٔ اول تیک زده (فعال و تمام‌نشده)"""

    serializer_class = FestivalListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Festival.objects.featured().order_by("display_order", "-registration_start")

    @extend_schema(
        summary="جشنواره‌های صفحه اول",
        description="جشنواره‌هایی که مدیر در پنل «نمایش در صفحه اول» را تیک زده است؛ مستقل از بقیهٔ جشنواره‌ها و مرتب بر اساس ترتیب نمایش.",
        tags=["Festivals"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FestivalDetailView(generics.RetrieveAPIView):
    """جزئیات یک جشنواره (قالب‌ها، محورها، قوانین آپلود، شناسهٔ ثبت‌نام کاربر)"""

    serializer_class = FestivalDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        return Festival.objects.filter(is_active=True)

    @extend_schema(summary="جزئیات جشنواره", tags=["Festivals"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FestivalRegisterView(APIView):
    """ثبت‌نام کاربر واردشده در یک جشنواره (یک‌بار؛ بعد از آن فقط اثر اضافه می‌شود)"""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="ثبت‌نام در جشنواره",
        description=(
            "فقط اطلاعات شخصی. قالب و محور هنگام ارسال هر اثر انتخاب می‌شود. "
            "اگر کاربر قبلاً ثبت‌نام کرده باشد ۴۰۹ با `registration_id` برمی‌گردد."
        ),
        request=MyRegistrationCreateSerializer,
        responses={201: FestivalRegistrationSerializer},
        tags=["Festivals"],
    )
    def post(self, request, id):
        festival = get_object_or_404(Festival, id=id, is_active=True)
        ensure_festival_open(festival)
        serializer = MyRegistrationCreateSerializer(
            data=request.data, context={"request": request, "festival": festival}
        )
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()
        return Response(
            {
                "message": "ثبت نام با موفقیت انجام شد",
                "data": FestivalRegistrationSerializer(
                    registration, context={"request": request}
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


class FestivalMyWorksView(generics.ListAPIView):
    """آثار من در یک جشنواره"""

    serializer_class = WorkListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Work.objects.filter(
                festival_registration__user=self.request.user,
                festival_registration__festival_id=self.kwargs["id"],
            )
            .select_related(
                "festival_registration",
                "festival_registration__festival",
                "festival_format",
                "festival_topic",
                "special_section",
            )
            .prefetch_related("files")
            .order_by("-created_at")
        )

    @extend_schema(summary="آثار من در این جشنواره", tags=["Festivals"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MyFestivalsView(generics.ListAPIView):
    """«جشنواره‌های من»: همهٔ جشنواره‌هایی که کاربر در آن‌ها ثبت‌نام کرده، یک‌جا"""

    serializer_class = MyFestivalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            FestivalRegistration.objects.filter(
                user=self.request.user, festival__isnull=False
            )
            .select_related("festival")
            .annotate(
                works_count=Count("works", distinct=True),
                submitted_works_count=Count(
                    "works", filter=~Q(works__status=Work.STATUS_DRAFT), distinct=True
                ),
            )
            .order_by("-festival__registration_start", "-created_at")
        )

    @extend_schema(
        summary="جشنواره‌های من",
        description="هر جشنواره‌ای که کاربر در آن ثبت‌نام کرده، با شناسهٔ ثبت‌نام و تعداد آثار.",
        tags=["Festivals"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UploadRulesView(APIView):
    """قوانین آپلود (نوع و سقف حجم هر نوع، حداکثر فایل هر اثر) برای راهنمای فرم"""

    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="قوانین آپلود فایل", tags=["Festivals"])
    def get(self, request):
        return Response(upload_rules())
