"""
Judging Views
پنل داور (فهرست آثار قابل داوری، ثبت امتیاز) و فهرست آثار داوری‌شده برای مدیر
"""
from decimal import Decimal

from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, serializers, status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from festival.judging import (
    IsJudge,
    WorkNotReviewable,
    assigned_works,
    reviewable_works,
    submit_review,
)
from festival.models import Review, Work
from festival.serializers import (
    FestivalBriefSerializer,
    FestivalFormatSerializer,
    FestivalTopicSerializer,
    FestivalSpecialSectionSerializer,
    WorkFileSerializer,
)

WORK_RELATIONS = (
    "festival_registration__festival",
    "festival_format",
    "festival_topic",
    "special_section",
)


class JudgeWorkSerializer(serializers.ModelSerializer):
    """اثر برای داور: بدون هویت سازنده (داوری کور)"""

    festival = FestivalBriefSerializer(source="festival_registration.festival", read_only=True)
    festival_max_score = serializers.IntegerField(
        source="festival_registration.festival.max_score", read_only=True
    )
    festival_format = FestivalFormatSerializer(read_only=True)
    festival_topic = FestivalTopicSerializer(read_only=True)
    special_section = FestivalSpecialSectionSerializer(read_only=True)
    files = WorkFileSerializer(many=True, read_only=True)
    my_review = serializers.SerializerMethodField()
    judging_form = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = [
            "id",
            "title",
            "description",
            "publish_link",
            "festival",
            "festival_max_score",
            "festival_format",
            "festival_topic",
            "special_section",
            "files",
            "my_review",
            "judging_form",
            "created_at",
        ]
        read_only_fields = fields

    def get_judging_form(self, obj):
        """شناسهٔ فرم داوری فعال جشنواره (برای نمایش معیارها)؛ None اگر امتیاز ساده است"""
        forms = getattr(obj.festival_registration.festival, "forms", None)
        form = forms.filter(kind="judging", is_active=True).first() if forms is not None else None
        return form.id if form else None

    def get_my_review(self, obj):
        user = self.context["request"].user
        review = next((r for r in obj.reviews.all() if r.judge_id == user.id), None)
        return MyReviewBriefSerializer(review).data if review else None


class MyReviewBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "score", "note", "created_at"]
        read_only_fields = fields


class MyReviewSerializer(serializers.ModelSerializer):
    work = JudgeWorkSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "score", "note", "created_at", "work"]
        read_only_fields = fields


class ReviewCreateSerializer(serializers.Serializer):
    score = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=Decimal("0"),
        error_messages={
            "required": "امتیاز را وارد کنید.",
            "invalid": "امتیاز باید عدد باشد.",
            "min_value": "امتیاز نمی‌تواند منفی باشد.",
        },
    )
    note = serializers.CharField(required=False, allow_blank=True, max_length=5000)

    def validate_score(self, value):
        max_score = self.context["max_score"]
        if value > max_score:
            raise serializers.ValidationError(
                f"امتیاز هر داور حداکثر {max_score} است."
            )
        return value


class AdminReviewSerializer(serializers.ModelSerializer):
    judge_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ["id", "judge", "judge_name", "score", "note", "created_at"]
        read_only_fields = fields

    def get_judge_name(self, obj):
        return str(obj.judge)


class AdminJudgedWorkSerializer(serializers.ModelSerializer):
    """اثر داوری‌شده برای مدیر: با هویت سازنده، امتیاز نهایی و ریز امتیاز داوران"""

    festival = FestivalBriefSerializer(source="festival_registration.festival", read_only=True)
    author_name = serializers.CharField(source="festival_registration.full_name", read_only=True)
    author_phone = serializers.CharField(source="festival_registration.phone_number", read_only=True)
    media_name = serializers.CharField(source="festival_registration.media_name", read_only=True)
    festival_format = serializers.CharField(source="festival_format.name", read_only=True, default=None)
    festival_topic = serializers.CharField(source="festival_topic.name", read_only=True, default=None)
    reviews = AdminReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Work
        fields = [
            "id",
            "title",
            "festival",
            "author_name",
            "author_phone",
            "media_name",
            "festival_format",
            "festival_topic",
            "status",
            "reviews_count",
            "final_score",
            "reviews",
            "created_at",
        ]
        read_only_fields = fields


class JudgeWorkListView(generics.ListAPIView):
    """آثاری که این داور هنوز می‌تواند داوری کند (امتیاز نداده و داوری‌شان کامل نشده)"""

    serializer_class = JudgeWorkSerializer
    permission_classes = [IsJudge]
    filter_backends = [OrderingFilter]
    ordering_fields = ["created_at", "title"]
    ordering = ["created_at"]

    def get_queryset(self):
        return (
            reviewable_works(self.request.user)
            .select_related(*WORK_RELATIONS)
            .prefetch_related("files", "reviews")
        )

    @extend_schema(
        summary="آثار قابل داوری من",
        description="`ordering`: created_at یا title (با - برای نزولی). آثاری که امتیاز داده‌اید یا داوری‌شان کامل شده نمایش داده نمی‌شود.",
        tags=["Judging"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class JudgeWorkDetailView(generics.RetrieveAPIView):
    serializer_class = JudgeWorkSerializer
    permission_classes = [IsJudge]

    def get_queryset(self):
        return (
            assigned_works(self.request.user)
            .select_related(*WORK_RELATIONS)
            .prefetch_related("files", "reviews")
        )

    @extend_schema(summary="جزئیات اثر برای داور", tags=["Judging"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class JudgeReviewCreateView(APIView):
    permission_classes = [IsJudge]

    @extend_schema(
        summary="ثبت امتیاز",
        description="هر داور به هر اثر یک‌بار امتیاز می‌دهد (۰ تا سقف جشنواره). امتیاز نهایی اثر مجموع امتیاز داوران است.",
        request=ReviewCreateSerializer,
        responses={201: MyReviewBriefSerializer},
        tags=["Judging"],
    )
    def post(self, request, pk):
        work = (
            assigned_works(request.user)
            .select_related("festival_registration__festival")
            .filter(pk=pk)
            .first()
        )
        if work is None:
            raise WorkNotReviewable("اثر پیدا نشد یا اجازهٔ داوری آن را ندارید.")
        festival = work.festival_registration.festival
        forms = getattr(festival, "forms", None)  # رابطهٔ معکوس از اپ formbuilder
        if forms is not None and forms.filter(kind="judging", is_active=True).exists():
            raise serializers.ValidationError(
                "این جشنواره فرم داوری دارد؛ امتیاز را از طریق فرم داوری ثبت کنید."
            )
        serializer = ReviewCreateSerializer(
            data=request.data,
            context={"max_score": work.festival_registration.festival.max_score},
        )
        serializer.is_valid(raise_exception=True)
        review = submit_review(
            judge=request.user,
            work_id=pk,
            score=serializer.validated_data["score"],
            note=serializer.validated_data.get("note", ""),
        )
        return Response(
            MyReviewBriefSerializer(review).data, status=status.HTTP_201_CREATED
        )


class JudgeMyReviewsView(generics.ListAPIView):
    """امتیازهایی که این داور داده"""

    serializer_class = MyReviewSerializer
    permission_classes = [IsJudge]

    def get_queryset(self):
        return (
            Review.objects.filter(judge=self.request.user)
            .select_related(*("work__" + r for r in WORK_RELATIONS))
            .prefetch_related("work__files", "work__reviews")
            .order_by("-created_at")
        )

    @extend_schema(summary="امتیازهای من", tags=["Judging"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdminJudgedWorksView(generics.ListAPIView):
    """آثاری که داوری‌شان کامل شده، با امتیاز نهایی (مجموع امتیاز داوران)؛ فقط مدیر"""

    serializer_class = AdminJudgedWorkSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [OrderingFilter]
    ordering_fields = ["final_score", "created_at", "title"]
    ordering = ["-final_score"]

    def get_queryset(self):
        queryset = (
            Work.objects.filter(status=Work.STATUS_JUDGED)
            .select_related(*WORK_RELATIONS, "festival_registration")
            .prefetch_related("reviews__judge")
        )
        festival_id = self.request.query_params.get("festival")
        if festival_id and festival_id.isdigit():
            queryset = queryset.filter(festival_registration__festival_id=int(festival_id))
        return queryset

    @extend_schema(
        summary="آثار داوری‌شده (مدیر)",
        description="`festival`: شناسه جشنواره. `ordering`: final_score، created_at، title (پیش‌فرض امتیاز نزولی).",
        tags=["Judging"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
