"""
Base Views for Content Models
Common view functionality
"""
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from config.pagination import StandardPagination
from django.db.models import F


class BaseContentListView(generics.ListAPIView):
    """
    Base API view for listing content with pagination, search, and filtering
    """

    pagination_class = StandardPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["publish_date", "tags__name"]
    search_fields = ["title", "description"]
    ordering_fields = ["publish_date", "created_at", "view_count"]
    ordering = ["-publish_date"]


class BaseContentDetailView(generics.RetrieveAPIView):
    """
    Base API view for retrieving content details
    Automatically increments view_count when accessed
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to increment view count"""
        instance = self.get_object()

        # Increment view count atomically
        instance.__class__.objects.filter(pk=instance.pk).update(
            view_count=F("view_count") + 1
        )

        # Refresh the instance to get the updated view_count
        instance.refresh_from_db()

        serializer = self.get_serializer(instance)
        return self.get_response(serializer.data)

    def get_response(self, data):
        """Helper method to return response - can be overridden"""
        from rest_framework.response import Response

        return Response(data)
