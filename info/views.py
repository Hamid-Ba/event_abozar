"""
Info App Views
API views for ContactUs and other info models
"""
from rest_framework import generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import ContactUs
from .serializers import ContactUsSerializer


@extend_schema_view(
    post=extend_schema(
        summary="ارسال پیام تماس",
        description="ارسال پیام تماس با ما از طریف فرم تماس",
        tags=["تماس با ما"],
        responses={201: ContactUsSerializer, 400: "خطای اعتبارسنجی"},
    )
)
class ContactUsCreateView(generics.CreateAPIView):
    """
    API view for creating contact us messages
    نمای API برای ایجاد پیام‌های تماس با ما
    """

    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer

    def create(self, request, *args, **kwargs):
        """Create contact message with custom response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the contact message
        contact = serializer.save()

        # TODO: Send email notification to admin
        # TODO: Send confirmation email to user

        return Response(serializer.data, status=status.HTTP_201_CREATED)
