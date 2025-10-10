"""
Festival Registration Serializers
"""
from rest_framework import serializers
from festival.models import FestivalRegistration
from festival.services import create_festival_registration
from province.serializers import ProvinceSerializer, CitySerializer


class FestivalRegistrationSerializer(serializers.ModelSerializer):
    """Festival Registration Serializer"""

    province = ProvinceSerializer(read_only=True)
    city = CitySerializer(read_only=True)

    class Meta:
        model = FestivalRegistration
        fields = [
            "id",
            "full_name",
            "father_name",
            "national_id",
            "gender",
            "education",
            "phone_number",
            "virtual_number",
            "province",
            "city",
            "media_name",
            "festival_format",
            "festival_topic",
            "special_section",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_national_id(self, value):
        """Validate Iranian national ID"""
        if len(value) != 10:
            raise serializers.ValidationError("کد ملی باید 10 رقم باشد")

        if not value.isdigit():
            raise serializers.ValidationError("کد ملی باید فقط شامل اعداد باشد")

        return value

    def validate_phone_number(self, value):
        """Validate Iranian phone number"""
        if len(value) != 11:
            raise serializers.ValidationError("شماره تماس باید 11 رقم باشد")

        if not value.startswith("09"):
            raise serializers.ValidationError("شماره تماس باید با 09 شروع شود")

        if not value.isdigit():
            raise serializers.ValidationError("شماره تماس باید فقط شامل اعداد باشد")

        return value


class FestivalRegistrationCreateSerializer(serializers.ModelSerializer):
    """Festival Registration Create Serializer"""

    province_id = serializers.IntegerField(write_only=True)
    city_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FestivalRegistration
        fields = [
            "full_name",
            "father_name",
            "national_id",
            "gender",
            "education",
            "phone_number",
            "virtual_number",
            "province_id",
            "city_id",
            "media_name",
            "festival_format",
            "festival_topic",
            "special_section",
        ]

    def validate_national_id(self, value):
        """Validate Iranian national ID"""
        if len(value) != 10:
            raise serializers.ValidationError("کد ملی باید 10 رقم باشد")

        if not value.isdigit():
            raise serializers.ValidationError("کد ملی باید فقط شامل اعداد باشد")

        return value

    def validate_phone_number(self, value):
        """Validate Iranian phone number"""
        if len(value) != 11:
            raise serializers.ValidationError("شماره تماس باید 11 رقم باشد")

        if not value.startswith("09"):
            raise serializers.ValidationError("شماره تماس باید با 09 شروع شود")

        if not value.isdigit():
            raise serializers.ValidationError("شماره تماس باید فقط شامل اعداد باشد")

        return value

    def validate(self, data):
        """Cross field validation"""
        from province.models import Province, City

        province_id = data.get("province_id")
        city_id = data.get("city_id")

        if province_id and city_id:
            try:
                province = Province.objects.get(id=province_id)
                city = City.objects.get(id=city_id)

                if city.province != province:
                    raise serializers.ValidationError(
                        "شهر انتخابی متعلق به استان انتخابی نیست"
                    )

            except Province.DoesNotExist:
                raise serializers.ValidationError("استان انتخابی وجود ندارد")
            except City.DoesNotExist:
                raise serializers.ValidationError("شهر انتخابی وجود ندارد")

        return data

    def create(self, validated_data):
        """Create festival registration with user creation"""
        phone_number = validated_data["phone_number"]

        # Convert province_id and city_id to province and city objects
        province_id = validated_data.pop("province_id")
        city_id = validated_data.pop("city_id")

        from province.models import Province, City

        validated_data["province"] = Province.objects.get(id=province_id)
        validated_data["city"] = City.objects.get(id=city_id)

        registration, user_created = create_festival_registration(
            phone_number=phone_number, registration_data=validated_data
        )
        return registration


class FestivalRegistrationListSerializer(serializers.ModelSerializer):
    """Festival Registration List Serializer - lighter version for lists"""

    user_phone = serializers.CharField(source="user.phone", read_only=True)
    province_name = serializers.CharField(source="province.name", read_only=True)
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = FestivalRegistration
        fields = [
            "id",
            "full_name",
            "media_name",
            "festival_format",
            "festival_topic",
            "province_name",
            "city_name",
            "user_phone",
            "created_at",
        ]
