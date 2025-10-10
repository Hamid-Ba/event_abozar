"""
Education Views
API views for Education model
"""
from drf_spectacular.utils import extend_schema, extend_schema_view
from .base import BaseContentListView, BaseContentDetailView
from content.models import Education
from content.serializers import EducationSerializer, EducationListSerializer


@extend_schema_view(
    get=extend_schema(
        summary="دریافت لیست آموزش‌ها",
        description="دریافت لیست صفحه‌بندی شده آموزش‌ها با قابلیت جستجو و فیلتر",
        tags=["آموزش"],
    )
)
class EducationListView(BaseContentListView):
    """
    API view for listing education content with pagination, search, and filtering
    """

    queryset = Education.objects.all()
    serializer_class = EducationListSerializer


@extend_schema_view(
    get=extend_schema(
        summary="دریافت جزئیات آموزش",
        description="دریافت جزئیات کامل یک آموزش",
        tags=["آموزش"],
    )
)
class EducationDetailView(BaseContentDetailView):
    """
    API view for retrieving education details
    """

    queryset = Education.objects.all()
    serializer_class = EducationSerializer
