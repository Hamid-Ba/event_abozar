"""
Festival Category Views
نماهای دسته‌بندی جشنواره - قالب‌ها، محورها و بخش‌های ویژه
"""
from rest_framework import generics
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from festival.models import FestivalFormat, FestivalTopic, FestivalSpecialSection
from festival.serializers import (
    FestivalFormatSerializer,
    FestivalTopicSerializer,
    FestivalSpecialSectionSerializer,
)


@extend_schema(
    tags=["Festival Categories"],
    summary="لیست قالب‌های جشنواره",
    description="دریافت لیست تمام قالب‌های فعال جشنواره رسانه‌ای ابوذر",
    parameters=[
        OpenApiParameter(
            name="is_active",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="فیلتر بر اساس وضعیت فعال/غیرفعال (پیش‌فرض: فقط فعال‌ها)",
            required=False,
        ),
    ],
)
class FestivalFormatListView(generics.ListAPIView):
    """
    Festival Format List API
    لیست قالب‌های جشنواره

    Returns a list of all active festival formats.
    برمی‌گرداند لیست تمام قالب‌های فعال جشنواره را.
    """

    serializer_class = FestivalFormatSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Get active festival formats ordered by display_order and name
        دریافت قالب‌های فعال مرتب شده بر اساس اولویت نمایش و نام
        """
        queryset = FestivalFormat.objects.all()

        # Filter by is_active (default: True)
        is_active = self.request.query_params.get("is_active", "true")
        if is_active.lower() in ["true", "1", "yes"]:
            queryset = queryset.filter(is_active=True)
        elif is_active.lower() in ["false", "0", "no"]:
            queryset = queryset.filter(is_active=False)

        return queryset.order_by("display_order", "name")


@extend_schema(
    tags=["Festival Categories"],
    summary="لیست محورهای جشنواره",
    description="دریافت لیست تمام محورهای فعال جشنواره رسانه‌ای ابوذر",
    parameters=[
        OpenApiParameter(
            name="is_active",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="فیلتر بر اساس وضعیت فعال/غیرفعال (پیش‌فرض: فقط فعال‌ها)",
            required=False,
        ),
    ],
)
class FestivalTopicListView(generics.ListAPIView):
    """
    Festival Topic List API
    لیست محورهای جشنواره

    Returns a list of all active festival topics.
    برمی‌گرداند لیست تمام محورهای فعال جشنواره را.
    """

    serializer_class = FestivalTopicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Get active festival topics ordered by display_order and name
        دریافت محورهای فعال مرتب شده بر اساس اولویت نمایش و نام
        """
        queryset = FestivalTopic.objects.all()

        # Filter by is_active (default: True)
        is_active = self.request.query_params.get("is_active", "true")
        if is_active.lower() in ["true", "1", "yes"]:
            queryset = queryset.filter(is_active=True)
        elif is_active.lower() in ["false", "0", "no"]:
            queryset = queryset.filter(is_active=False)

        return queryset.order_by("display_order", "name")


@extend_schema(
    tags=["Festival Categories"],
    summary="لیست بخش‌های ویژه جشنواره",
    description="دریافت لیست تمام بخش‌های ویژه فعال جشنواره رسانه‌ای ابوذر",
    parameters=[
        OpenApiParameter(
            name="is_active",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="فیلتر بر اساس وضعیت فعال/غیرفعال (پیش‌فرض: فقط فعال‌ها)",
            required=False,
        ),
    ],
)
class FestivalSpecialSectionListView(generics.ListAPIView):
    """
    Festival Special Section List API
    لیست بخش‌های ویژه جشنواره

    Returns a list of all active festival special sections.
    برمی‌گرداند لیست تمام بخش‌های ویژه فعال جشنواره را.
    """

    serializer_class = FestivalSpecialSectionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Get active special sections ordered by display_order and name
        دریافت بخش‌های ویژه فعال مرتب شده بر اساس اولویت نمایش و نام
        """
        queryset = FestivalSpecialSection.objects.all()

        # Filter by is_active (default: True)
        is_active = self.request.query_params.get("is_active", "true")
        if is_active.lower() in ["true", "1", "yes"]:
            queryset = queryset.filter(is_active=True)
        elif is_active.lower() in ["false", "0", "no"]:
            queryset = queryset.filter(is_active=False)

        return queryset.order_by("display_order", "name")
