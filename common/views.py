from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiExample

User = get_user_model()


class CreateSuperUserSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11, help_text="Phone number (11 digits)")
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(min_length=8)
    fullName = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Full name of the user",
    )

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "A user with this phone number already exists."
            )
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class CreateSuperUserView(APIView):
    """
    Create a superuser account for development purposes.

    This endpoint is intended for local development only.
    """

    @extend_schema(
        request=CreateSuperUserSerializer,
        responses={
            201: {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "user_id": {"type": "integer"},
                    "phone": {"type": "string"},
                    "email": {"type": "string"},
                    "fullName": {"type": "string"},
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "details": {"type": "object"},
                },
            },
        },
        examples=[
            OpenApiExample(
                "Create superuser example",
                value={
                    "phone": "09123456789",
                    "email": "admin@example.com",
                    "password": "secure-password-123",
                    "fullName": "Admin User",
                },
            )
        ],
    )
    def post(self, request):
        serializer = CreateSuperUserSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": "Validation failed", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validated_data = serializer.validated_data

            # Create superuser using the custom manager
            user = User.objects.create_superuser(
                phone=validated_data["phone"],
                email=validated_data.get("email", ""),
                password=validated_data["password"],
                fullName=validated_data.get("fullName", ""),
            )

            return Response(
                {
                    "message": "Superuser created successfully",
                    "user_id": user.id,
                    "phone": user.phone,
                    "email": user.email,
                    "fullName": user.fullName,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": "Failed to create superuser", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
