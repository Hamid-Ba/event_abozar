"""
Notification Views
"""
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from festival.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "kind", "title", "body", "object_id", "is_read", "created_at"]
        read_only_fields = fields


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        if self.request.query_params.get("unread") in ("1", "true"):
            queryset = queryset.filter(is_read=False)
        return queryset

    @extend_schema(summary="اعلان‌های من", tags=["Notifications"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class NotificationUnreadCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="تعداد اعلان‌های خوانده‌نشده", tags=["Notifications"])
    def get(self, request):
        return Response(
            {"unread": Notification.objects.filter(user=request.user, is_read=False).count()}
        )


class NotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="علامت‌گذاری اعلان به‌عنوان خوانده‌شده", tags=["Notifications"])
    def post(self, request, pk=None):
        queryset = Notification.objects.filter(user=request.user, is_read=False)
        if pk is not None:
            queryset = queryset.filter(pk=pk)
        updated = queryset.update(is_read=True)
        return Response({"updated": updated}, status=status.HTTP_200_OK)
