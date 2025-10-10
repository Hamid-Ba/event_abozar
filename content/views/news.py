"""
News Views
API views for News model
"""
from drf_spectacular.utils import extend_schema, extend_schema_view
from .base import BaseContentListView, BaseContentDetailView
from content.models import News
from content.serializers import NewsSerializer, NewsListSerializer


@extend_schema_view(
    get=extend_schema(
        summary="دریافت لیست اخبار",
        description="دریافت لیست صفحه‌بندی شده اخبار با قابلیت جستجو و فیلتر",
        tags=["اخبار"],
    )
)
class NewsListView(BaseContentListView):
    """
    API view for listing news with pagination, search, and filtering
    """

    queryset = News.objects.all()
    serializer_class = NewsListSerializer


@extend_schema_view(
    get=extend_schema(
        summary="دریافت جزئیات خبر",
        description="دریافت جزئیات کامل یک خبر",
        tags=["اخبار"],
    )
)
class NewsDetailView(BaseContentDetailView):
    """
    API view for retrieving news details
    """

    queryset = News.objects.all()
    serializer_class = NewsSerializer
