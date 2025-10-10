"""
Account Module Views
"""
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt import authentication
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, views


from rest_framework.response import Response
from account.serializers import (
    UserSerializer,
)
from monitoring.models.observability import CodeLog

from . import services


class LoginOrRegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    class InputSerializer(serializers.Serializer):
        phone = serializers.CharField(
            max_length=11,
            required=True,
            error_messages={
                "blank": "موبایل خود را وارد نمایید",
                "required": "موبایل خود را وارد نمایید",
            },
        )

        def validate(self, attrs):
            phone = attrs.get("phone")
            if not phone.isdigit():
                return super().validate(attrs)
            return attrs

    @extend_schema(request=InputSerializer, responses=InputSerializer)
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        if serializer.is_valid():
            otp = services.generate_otp(phone=serializer.validated_data.get("phone"))
            return Response(
                {
                    "message": "OTP Has Been Sent Successfully",
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthTokenView(views.APIView):
    """Auth Token View For Create JWT Token"""

    class AuthTokenSerializer(serializers.Serializer):
        phone = serializers.CharField(
            max_length=11,
            required=True,
            error_messages={
                "blank": "موبایل خود را وارد نمایید",
                "required": "موبایل خود را وارد نمایید",
            },
        )
        password = serializers.CharField(
            required=True,
            error_messages={
                "blank": "رمزعبور خود را وارد نمایید",
                "required": "رمزعبور خود را وارد نمایید",
            },
        )

    @extend_schema(request=AuthTokenSerializer, responses=AuthTokenSerializer)
    def post(self, request):
        serializer = self.AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data.get("phone")
            otp = serializer.validated_data.get("password")

            is_verify = services.verify_otp(phone, otp)

            if is_verify:
                services.get_or_create_user(phone, otp)
                try:
                    refresh = services.generate_jwt(phone)

                    return Response(
                        {
                            "phone": phone,
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                        status=status.HTTP_201_CREATED,
                    )
                except:
                    return Response(
                        {"message": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
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
