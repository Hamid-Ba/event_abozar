"""
Base Views for Content Models
Common view functionality
"""
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from config.pagination import StandardPagination


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
    ordering_fields = ["publish_date", "created_at"]
    ordering = ["-publish_date"]


class BaseContentDetailView(generics.RetrieveAPIView):
    """
    Base API view for retrieving content details
    """

    permission_classes = [IsAuthenticatedOrReadOnly]
