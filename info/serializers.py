"""
Info App Serializers
Serializers for ContactUs and other info models
"""
from rest_framework import serializers
from .models import ContactUs


class ContactUsSerializer(serializers.ModelSerializer):
    """
    Serializer for ContactUs model
    سریالایزر برای مدل تماس با ما
    """

    class Meta:
        model = ContactUs
        fields = ["id", "full_name", "phone", "email", "message", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_phone(self, value):
        """Additional phone validation"""
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
            raise serializers.ValidationError("نام کامل باید حداقل 2 کاراکتر باشد")
        return value.strip()

    def validate_message(self, value):
        """Validate message"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("پیام باید حداقل 10 کاراکتر باشد")
        return value.strip()
