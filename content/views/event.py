"""
Event Views
API views for Event model
"""
from drf_spectacular.utils import extend_schema, extend_schema_view
from .base import BaseContentListView, BaseContentDetailView
from content.models import Event
from content.serializers import EventSerializer, EventListSerializer


@extend_schema_view(
    get=extend_schema(
        summary="دریافت لیست رویدادها",
        description="دریافت لیست صفحه‌بندی شده رویدادها با قابلیت جستجو و فیلتر",
        tags=["رویداد"],
    )
)
class EventListView(BaseContentListView):
    """
    API view for listing events with pagination, search, and filtering
    """

    queryset = Event.objects.all()
    serializer_class = EventListSerializer


@extend_schema_view(
    get=extend_schema(
        summary="دریافت جزئیات رویداد",
        description="دریافت جزئیات کامل یک رویداد",
        tags=["رویداد"],
    )
)
class EventDetailView(BaseContentDetailView):
    """
    API view for retrieving event details
    """

    queryset = Event.objects.all()
    serializer_class = EventSerializer
