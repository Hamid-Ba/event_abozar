"""
Work Views
"""
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from festival.models import Work, FestivalRegistration
from festival.serializers import (
    WorkListSerializer,
    WorkDetailSerializer,
    WorkCreateSerializer,
    WorkFileSerializer,
    WorkFilesAddSerializer,
)
from festival.services import (
    attach_files,
    ensure_work_editable,
    refresh_work_status_after_file_removal,
)
from festival.models import WorkFile


def _work_queryset(user):
    """آثار کاربر با همهٔ روابط لازم برای نمایش (بدون N+1)"""
    return (
        Work.objects.filter(festival_registration__user=user)
        .select_related(
            "festival_registration",
            "festival_registration__festival",
            "festival_registration__province",
            "festival_registration__city",
            "festival_format",
            "festival_topic",
            "special_section",
        )
        .prefetch_related("files")
    )


class WorkListCreateView(generics.ListCreateAPIView):
    """List and Create Works - Authenticated Users Only"""

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "festival_registration",
        "festival_registration__festival",
        "festival_format",
        "festival_topic",
        "status",
    ]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Return only works belonging to the authenticated user"""
        return _work_queryset(self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.request.method == "POST":
            return WorkCreateSerializer
        return WorkListSerializer

    @extend_schema(
        summary="فهرست آثار کاربر",
        description="دریافت فهرست آثار ثبت شده توسط کاربر احراز هویت شده",
        tags=["Works"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="ایجاد اثر جدید",
        description=(
            "ثبت اثر جدید برای ثبت‌نام کاربر. قالب/محور روی خود اثر است. "
            "فایل‌ها با فیلد تکراری `files` (چند فایل) ارسال می‌شوند یا بعداً با `works/<id>/files/`. "
            "اثر بدون فایل «پیش‌نویس» است."
        ),
        request=WorkCreateSerializer,
        responses={201: WorkDetailSerializer},
        tags=["Works"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        work = serializer.save()
        # پاسخ کامل (شامل id و فایل‌ها) تا فرانت بتواند فایل‌های بعدی را اضافه کند
        work = _work_queryset(request.user).get(pk=work.pk)
        return Response(
            WorkDetailSerializer(work, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )


class WorkDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, Update, Delete Work - Authenticated Users Only"""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Return only works belonging to the authenticated user"""
        return _work_queryset(self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.request.method in ["PUT", "PATCH"]:
            return WorkCreateSerializer
        return WorkDetailSerializer

    @extend_schema(
        summary="جزئیات اثر",
        description="دریافت جزئیات کامل یک اثر",
        tags=["Works"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance = self.get_queryset().get(pk=instance.pk)
        return Response(
            WorkDetailSerializer(instance, context=self.get_serializer_context()).data
        )

    def perform_destroy(self, instance):
        ensure_work_editable(instance)
        instance.delete()

    @extend_schema(
        summary="به‌روزرسانی اثر",
        description="به‌روزرسانی اطلاعات یک اثر. کاربر تنها می‌تواند آثار خود را ویرایش کند.",
        tags=["Works"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="به‌روزرسانی جزئی اثر",
        description="به‌روزرسانی جزئی اطلاعات یک اثر",
        tags=["Works"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="حذف اثر",
        description="حذف یک اثر. کاربر تنها می‌تواند آثار خود را حذف کند.",
        tags=["Works"],
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class UserFestivalRegistrationsView(generics.ListAPIView):
    """Get User's Festival Registrations - for selecting in work creation"""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        from festival.serializers import FestivalRegistrationListSerializer

        return FestivalRegistrationListSerializer

    def get_queryset(self):
        """Return only festival registrations belonging to the authenticated user"""
        user = self.request.user
        return FestivalRegistration.objects.filter(user=user).select_related(
            "province", "city", "festival"
        )

    @extend_schema(
        summary="فهرست ثبت نام‌های کاربر",
        description="دریافت فهرست ثبت نام‌های جشنواره متعلق به کاربر احراز هویت شده برای انتخاب در ایجاد اثر",
        tags=["Festival Registration"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class WorkByFestivalView(generics.ListAPIView):
    """List works by festival registration id for authenticated user"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        festival_id = self.kwargs.get("festival_id")
        return _work_queryset(user).filter(festival_registration_id=festival_id)

    @extend_schema(
        summary="فهرست آثار بر اساس ثبت‌نام جشنواره",
        description="دریافت فهرست آثار ثبت شده توسط کاربر برای یک ثبت‌نام جشنواره خاص (با festival_id)",
        tags=["Works"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class WorkFilesView(APIView):
    """افزودن فایل به اثر (مرحلهٔ دوم آپلود)"""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="افزودن فایل به اثر",
        description=(
            "یک یا چند فایل (`files`) یا یک فایل (`file`). نوع و حجم هر فایل بررسی می‌شود و "
            "در صورت خطا پیام فارسی با نام فایل و حجم/سقف مجاز برمی‌گردد."
        ),
        request=WorkFilesAddSerializer,
        responses={201: WorkFileSerializer(many=True)},
        tags=["Works"],
    )
    def post(self, request, pk):
        work = get_object_or_404(_work_queryset(request.user), pk=pk)
        serializer = WorkFilesAddSerializer(
            data=request.data, context={"request": request, "work": work}
        )
        serializer.is_valid(raise_exception=True)
        created = attach_files(work, serializer.validated_data["uploaded_files"])
        return Response(
            WorkFileSerializer(created, many=True, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class WorkFileDetailView(APIView):
    """حذف یک فایل از اثر"""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="حذف فایل اثر", tags=["Works"])
    def delete(self, request, pk, file_id):
        work = get_object_or_404(_work_queryset(request.user), pk=pk)
        ensure_work_editable(work)
        work_file = get_object_or_404(WorkFile, pk=file_id, work=work)
        work_file.delete()
        refresh_work_status_after_file_removal(work)
        return Response(status=status.HTTP_204_NO_CONTENT)
