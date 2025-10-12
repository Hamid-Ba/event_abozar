"""
Account Module Views
"""
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt import authentication
from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, permissions, views
from django.contrib.auth.hashers import make_password

from rest_framework.response import Response
from account.serializers import (
    UserSerializer,
)
from monitoring.models.observability import CodeLog

from . import services

User = get_user_model()


class RegisterView(views.APIView):
    """User Registration View"""

    permission_classes = [permissions.AllowAny]

    class RegisterSerializer(serializers.Serializer):
        full_name = serializers.CharField(
            max_length=255,
            required=True,
            error_messages={
                "blank": "نام کامل خود را وارد نمایید",
                "required": "نام کامل خود را وارد نمایید",
            },
        )
        phone = serializers.CharField(
            max_length=11,
            required=True,
            error_messages={
                "blank": "شماره تلفن خود را وارد نمایید",
                "required": "شماره تلفن خود را وارد نمایید",
            },
        )
        password = serializers.CharField(
            min_length=6,
            required=True,
            error_messages={
                "blank": "رمز عبور خود را وارد نمایید",
                "required": "رمز عبور خود را وارد نمایید",
                "min_length": "رمز عبور باید حداقل ۶ کاراکتر باشد",
            },
        )

        def validate_phone(self, value):
            """Validate Iranian phone number"""
            if not value.startswith("09"):
                raise serializers.ValidationError("شماره تلفن باید با 09 شروع شود")
            if len(value) != 11:
                raise serializers.ValidationError("شماره تلفن باید 11 رقم باشد")
            if not value.isdigit():
                raise serializers.ValidationError("شماره تلفن باید فقط شامل اعداد باشد")
            return value

        def validate_full_name(self, value):
            """Validate full name"""
            if len(value.strip()) < 2:
                raise serializers.ValidationError("نام کامل باید حداقل ۲ کاراکتر باشد")
            return value.strip()

    @extend_schema(
        request=RegisterSerializer,
        summary="ثبت نام کاربر",
        description="ثبت نام کاربر جدید با نام کامل، شماره تلفن و رمز عبور. اگر کاربر با این شماره تلفن وجود داشته باشد، رمز عبور جدید برای او اعمال می‌شود.",
        tags=["Authentication"],
        responses={
            201: {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "phone": {"type": "string"},
                            "full_name": {"type": "string"},
                        },
                    },
                },
            },
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    )
    def post(self, request):
        serializer = self.RegisterSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data.get("phone")
            full_name = serializer.validated_data.get("full_name")
            password = serializer.validated_data.get("password")

            try:
                # Check if user exists (might be from festival registration)
                user, created = User.objects.get_or_create(
                    phone=phone,
                    defaults={
                        "fullName": full_name,
                    },
                )

                # Only update fullName for new users, but always update password
                if created:
                    user.fullName = full_name
                user.set_password(password)
                user.save()

                if created:
                    message = "کاربر با موفقیت ثبت نام شد"
                else:
                    message = "رمز عبور کاربر با موفقیت به‌روزرسانی شد"

                return Response(
                    {
                        "message": message,
                        "user": {
                            "id": user.id,
                            "phone": user.phone,
                            "full_name": user.fullName,
                        },
                    },
                    status=status.HTTP_201_CREATED,
                )

            except Exception as e:
                return Response(
                    {"error": "خطا در ثبت نام کاربر"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    """User Login View"""

    permission_classes = [permissions.AllowAny]

    class LoginSerializer(serializers.Serializer):
        phone = serializers.CharField(
            max_length=11,
            required=True,
            error_messages={
                "blank": "شماره تلفن خود را وارد نمایید",
                "required": "شماره تلفن خود را وارد نمایید",
            },
        )
        password = serializers.CharField(
            required=True,
            error_messages={
                "blank": "رمز عبور خود را وارد نمایید",
                "required": "رمز عبور خود را وارد نمایید",
            },
        )

        def validate_phone(self, value):
            """Validate Iranian phone number"""
            if not value.startswith("09"):
                raise serializers.ValidationError("شماره تلفن باید با 09 شروع شود")
            if len(value) != 11:
                raise serializers.ValidationError("شماره تلفن باید 11 رقم باشد")
            if not value.isdigit():
                raise serializers.ValidationError("شماره تلفن باید فقط شامل اعداد باشد")
            return value

    @extend_schema(
        request=LoginSerializer,
        summary="ورود کاربر",
        description="ورود کاربر با شماره تلفن و رمز عبور و دریافت JWT توکن",
        tags=["Authentication"],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "phone": {"type": "string"},
                            "full_name": {"type": "string"},
                        },
                    },
                    "tokens": {
                        "type": "object",
                        "properties": {
                            "refresh": {"type": "string"},
                            "access": {"type": "string"},
                        },
                    },
                },
            },
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    )
    def post(self, request):
        serializer = self.LoginSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data.get("phone")
            password = serializer.validated_data.get("password")

            try:
                # Check if user exists
                user = User.objects.filter(phone=phone).first()
                if not user:
                    return Response(
                        {"error": "کاربری با این شماره تلفن یافت نشد"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Check if user has a password set
                if not user.password:
                    return Response(
                        {"error": "لطفاً ابتدا ثبت نام کنید"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Authenticate user
                if user.check_password(password):
                    # Generate JWT tokens
                    refresh = services.generate_jwt(phone)
                    if refresh:
                        return Response(
                            {
                                "message": "ورود با موفقیت انجام شد",
                                "user": {
                                    "id": user.id,
                                    "phone": user.phone,
                                    "full_name": user.fullName,
                                },
                                "tokens": {
                                    "refresh": str(refresh),
                                    "access": str(refresh.access_token),
                                },
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {"error": "خطا در تولید توکن"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    return Response(
                        {"error": "رمز عبور اشتباه است"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            except Exception as e:
                return Response(
                    {"error": "خطا در ورود کاربر"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(generics.RetrieveUpdateAPIView):
    """Retrieve Or Update APIView for User"""

    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """Retrieve The Authorized User"""
        return self.request.user
