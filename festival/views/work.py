"""
Work Views
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
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
)


class WorkListCreateView(generics.ListCreateAPIView):
    """List and Create Works - Authenticated Users Only"""

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "festival_registration__festival_format",
        "festival_registration__festival_topic",
    ]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Return only works belonging to the authenticated user"""
        user = self.request.user
        return Work.objects.filter(festival_registration__user=user).select_related(
            "festival_registration",
            "festival_registration__province",
            "festival_registration__city",
        )

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
        description="ثبت اثر جدید برای کاربر احراز هویت شده. کاربر تنها می‌تواند برای ثبت نام‌های خود اثر ایجاد کند.",
        tags=["Works"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Custom create logic"""
        serializer.save()


class WorkDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, Update, Delete Work - Authenticated Users Only"""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Return only works belonging to the authenticated user"""
        user = self.request.user
        return Work.objects.filter(festival_registration__user=user).select_related(
            "festival_registration",
            "festival_registration__province",
            "festival_registration__city",
        )

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
            "province", "city"
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
        return Work.objects.filter(
            festival_registration__user=user, festival_registration_id=festival_id
        ).select_related(
            "festival_registration",
            "festival_registration__province",
            "festival_registration__city",
        )

    @extend_schema(
        summary="فهرست آثار بر اساس ثبت‌نام جشنواره",
        description="دریافت فهرست آثار ثبت شده توسط کاربر برای یک ثبت‌نام جشنواره خاص (با festival_id)",
        tags=["Works"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
