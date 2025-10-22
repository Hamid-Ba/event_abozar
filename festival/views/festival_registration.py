"""
Festival Registration Views
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from django_filters import CharFilter
from rest_framework.filters import SearchFilter, OrderingFilter

from festival.models import FestivalRegistration, Work
from content.models import Event, Education, News
from festival.serializers import (
    FestivalRegistrationSerializer,
    FestivalRegistrationCreateSerializer,
    FestivalRegistrationListSerializer,
    MyFestivalRegistrationListSerializer,
    MyFestivalRegistrationDetailSerializer,
    StatisticsSerializer,
    MyStatisticsSerializer,
)
from province.models import Province, City
from province.serializers import ProvinceSerializer, CitySerializer


class FestivalRegistrationFilter(FilterSet):
    """Custom filter for FestivalRegistration to support filtering by code"""

    festival_format = CharFilter(field_name="festival_format__code")
    festival_topic = CharFilter(field_name="festival_topic__code")
    special_section = CharFilter(field_name="special_section__code")

    class Meta:
        model = FestivalRegistration
        fields = [
            "festival_format",
            "festival_topic",
            "special_section",
            "gender",
            "province",
            "city",
        ]


class FestivalRegistrationCreateView(generics.CreateAPIView):
    """Create Festival Registration - No Authentication Required"""

    serializer_class = FestivalRegistrationCreateSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="ثبت‌نام در جشنواره",
        description="ثبت‌نام جدید در یازدهمین جشنواره رسانه‌ای ابوذر. کاربر بر اساس شماره تلفن به صورت خودکار ایجاد می‌شود.",
        tags=["Festival Registration"],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if registration with this national_id already exists
        national_id = serializer.validated_data.get("national_id")
        # if FestivalRegistration.objects.filter(national_id=national_id).exists():
        #     return Response(
        #         {"error": "قبلاً با این کد ملی ثبت نام شده است"},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

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

    # Use custom filterset class
    filterset_class = FestivalRegistrationFilter

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
        summary="فهرست ثبت‌نام‌ها",
        description="دریافت فهرست کامل ثبت‌نام‌های جشنواره با قابلیت فیلتر و جستجو بر اساس نام، رسانه، استان، شهر و سایر فیلدها.",
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


class MyFestivalRegistrationListView(generics.ListAPIView):
    """List authenticated user's festival registrations"""

    serializer_class = MyFestivalRegistrationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # Use custom filterset class
    filterset_class = FestivalRegistrationFilter

    # Search fields
    search_fields = [
        "full_name",
        "media_name",
        "festival_format__name",
        "festival_topic__name",
    ]

    # Ordering
    ordering_fields = ["created_at", "full_name", "media_name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return only the authenticated user's festival registrations"""
        return FestivalRegistration.objects.select_related("province", "city").filter(
            user=self.request.user
        )

    @extend_schema(
        summary="فهرست ثبت‌نام‌های من",
        description="دریافت فهرست ثبت‌نام‌های جشنواره کاربر احراز هویت شده با قابلیت فیلتر و جستجو.",
        tags=["My Festival Registration"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MyFestivalRegistrationDetailView(generics.RetrieveAPIView):
    """Get authenticated user's festival registration detail"""

    serializer_class = MyFestivalRegistrationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        """Return only the authenticated user's festival registrations"""
        return FestivalRegistration.objects.select_related("province", "city").filter(
            user=self.request.user
        )

    @extend_schema(
        summary="جزئیات ثبت‌نام من",
        description="دریافت جزئیات کامل یک ثبت‌نام جشنواره متعلق به کاربر احراز هویت شده.",
        tags=["My Festival Registration"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StatisticsView(APIView):
    """Statistics API endpoint for festival, works, and content counts"""

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="آمار کلی سیستم",
        description="دریافت آمار کلی شامل تعداد کاربران ثبت نام شده در جشنواره، تعداد کل اثار ارسالی، و تعداد کل محتوا (اخبار، رویدادها، آموزش‌ها).",
        tags=["Statistics"],
        responses={200: StatisticsSerializer},
    )
    def get(self, request, *args, **kwargs):
        """Get system statistics"""

        # Count registered users in festival
        registered_users_count = FestivalRegistration.objects.count()

        # Count total works
        total_works_count = Work.objects.count()

        # Count all content (events, education, news)
        events_count = Event.objects.count()
        education_count = Education.objects.count()
        news_count = News.objects.count()
        content_count = events_count + education_count + news_count

        data = {
            "registered_users_count": registered_users_count,
            "total_works_count": total_works_count,
            "content_count": content_count,
        }

        serializer = StatisticsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyStatisticsView(APIView):
    """Authenticated user statistics API endpoint"""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="آمار شخصی من",
        description="دریافت آمار شخصی کاربر احراز هویت شده شامل تعداد ثبت‌نام‌های شخصی، تعداد آثار ارسالی شخصی، و تعداد کل محتوای سیستم.",
        tags=["My Statistics"],
        responses={200: MyStatisticsSerializer},
    )
    def get(self, request, *args, **kwargs):
        """Get authenticated user's personal statistics"""

        # Count user's festival registrations
        my_registrations_count = FestivalRegistration.objects.filter(
            user=request.user
        ).count()

        # Count user's works
        my_works_count = Work.objects.filter(
            festival_registration__user=request.user
        ).count()

        # Count total content (events, education, news) - same as global statistics
        events_count = Event.objects.count()
        education_count = Education.objects.count()
        news_count = News.objects.count()
        total_content_count = events_count + education_count + news_count

        data = {
            "my_registrations_count": my_registrations_count,
            "my_works_count": my_works_count,
            "total_content_count": total_content_count,
        }

        serializer = MyStatisticsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
