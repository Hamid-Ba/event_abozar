"""
Festival Registration Views
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from festival.models import FestivalRegistration
from festival.serializers import (
    FestivalRegistrationSerializer,
    FestivalRegistrationCreateSerializer,
    FestivalRegistrationListSerializer,
)
from province.models import Province, City
from province.serializers import ProvinceSerializer, CitySerializer


class FestivalRegistrationCreateView(generics.CreateAPIView):
    """Create Festival Registration - No Authentication Required"""

    serializer_class = FestivalRegistrationCreateSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Create Festival Registration",
        description="Create a new festival registration. User will be created automatically using phone number.",
        tags=["Festival Registration"],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if registration with this national_id already exists
        national_id = serializer.validated_data.get("national_id")
        if FestivalRegistration.objects.filter(national_id=national_id).exists():
            return Response(
                {"error": "قبلاً با این کد ملی ثبت نام شده است"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        registration = serializer.save()
        response_serializer = FestivalRegistrationSerializer(registration)

        return Response(
            {"message": "ثبت نام با موفقیت انجام شد", "data": response_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class FestivalRegistrationListView(generics.ListAPIView):
    """List Festival Registrations - No Authentication Required"""

    queryset = FestivalRegistration.objects.select_related(
        "user", "province", "city"
    ).all()
    serializer_class = FestivalRegistrationListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # Filter fields
    filterset_fields = [
        "festival_format",
        "festival_topic",
        "province",
        "city",
        "gender",
        "special_section",
    ]

    # Search fields
    search_fields = [
        "full_name",
        "media_name",
        "national_id",
        "province__name",
        "city__name",
    ]

    # Ordering
    ordering_fields = ["created_at", "full_name", "province__name", "city__name"]
    ordering = ["-created_at"]

    @extend_schema(
        summary="List Festival Registrations",
        description="Get list of all festival registrations with filtering and search capabilities.",
        tags=["Festival Registration"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FestivalRegistrationDetailView(generics.RetrieveAPIView):
    """Get Festival Registration Detail - No Authentication Required"""

    queryset = FestivalRegistration.objects.select_related(
        "user", "province", "city"
    ).all()
    serializer_class = FestivalRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"

    @extend_schema(
        summary="Get Festival Registration Detail",
        description="Get detailed information about a specific festival registration.",
        tags=["Festival Registration"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FestivalRegistrationSearchView(generics.ListAPIView):
    """Search Festival Registrations by Phone or National ID"""

    serializer_class = FestivalRegistrationListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        phone = self.request.query_params.get("phone", None)
        national_id = self.request.query_params.get("national_id", None)

        queryset = FestivalRegistration.objects.select_related(
            "user", "province", "city"
        ).none()

        if phone:
            queryset = FestivalRegistration.objects.select_related(
                "user", "province", "city"
            ).filter(phone_number=phone)
        elif national_id:
            queryset = FestivalRegistration.objects.select_related(
                "user", "province", "city"
            ).filter(national_id=national_id)

        return queryset

    @extend_schema(
        summary="Search Festival Registrations",
        description="Search festival registrations by phone number or national ID.",
        parameters=[
            {
                "name": "phone",
                "in": "query",
                "description": "Phone number to search for",
                "required": False,
                "schema": {"type": "string"},
            },
            {
                "name": "national_id",
                "in": "query",
                "description": "National ID to search for",
                "required": False,
                "schema": {"type": "string"},
            },
        ],
        tags=["Festival Registration"],
    )
    def get(self, request, *args, **kwargs):
        if not any(
            [request.query_params.get("phone"), request.query_params.get("national_id")]
        ):
            return Response(
                {"error": "لطفاً شماره تماس یا کد ملی را وارد کنید"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().get(request, *args, **kwargs)


class ProvinceListView(generics.ListAPIView):
    """List all provinces for form selection"""

    queryset = Province.objects.all().order_by("name")
    serializer_class = ProvinceSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="List Provinces",
        description="Get list of all provinces for dropdown selection in registration form.",
        tags=["Province & City"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CityListView(generics.ListAPIView):
    """List cities by province for form selection"""

    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        province_id = self.request.query_params.get("province_id")
        if province_id:
            try:
                province_id = int(province_id)
                return City.objects.filter(province_id=province_id).order_by("name")
            except (ValueError, TypeError):
                return City.objects.none()
        return City.objects.none()

    @extend_schema(
        summary="List Cities by Province",
        description="Get list of cities for a specific province.",
        parameters=[
            {
                "name": "province_id",
                "in": "query",
                "description": "Province ID to get cities for",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        tags=["Province & City"],
    )
    def get(self, request, *args, **kwargs):
        province_id = request.query_params.get("province_id")
        if not province_id:
            return Response(
                {"error": "لطفاً شناسه استان را وارد کنید"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().get(request, *args, **kwargs)
