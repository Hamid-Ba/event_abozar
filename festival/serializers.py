"""
Festival Registration Serializers
"""
from rest_framework import serializers
from festival.models import (
    FestivalRegistration,
    Work,
    FestivalFormat,
    FestivalTopic,
    FestivalSpecialSection,
)
from festival.services import create_festival_registration
from province.serializers import ProvinceSerializer, CitySerializer


class FestivalFormatSerializer(serializers.ModelSerializer):
    """Festival Format Serializer"""

    class Meta:
        model = FestivalFormat
        fields = ["id", "code", "name", "description"]


class FestivalTopicSerializer(serializers.ModelSerializer):
    """Festival Topic Serializer"""

    class Meta:
        model = FestivalTopic
        fields = ["id", "code", "name", "description"]


class FestivalSpecialSectionSerializer(serializers.ModelSerializer):
    """Festival Special Section Serializer"""

    class Meta:
        model = FestivalSpecialSection
        fields = ["id", "code", "name", "description"]


class FestivalRegistrationSerializer(serializers.ModelSerializer):
    """Festival Registration Serializer"""

    province = ProvinceSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    festival_format = FestivalFormatSerializer(read_only=True)
    festival_topic = FestivalTopicSerializer(read_only=True)
    special_section = FestivalSpecialSectionSerializer(read_only=True)

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

    # Accept code strings and convert to ForeignKey objects
    festival_format = serializers.SlugRelatedField(
        slug_field="code", queryset=FestivalFormat.objects.all()
    )
    festival_topic = serializers.SlugRelatedField(
        slug_field="code", queryset=FestivalTopic.objects.all()
    )
    special_section = serializers.SlugRelatedField(
        slug_field="code",
        queryset=FestivalSpecialSection.objects.all(),
        required=False,
        allow_null=True,
    )

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
    festival_format = FestivalFormatSerializer(read_only=True)
    festival_topic = FestivalTopicSerializer(read_only=True)
    special_section = FestivalSpecialSectionSerializer(read_only=True)

    class Meta:
        model = FestivalRegistration
        fields = [
            "id",
            "full_name",
            "media_name",
            "festival_format",
            "festival_topic",
            "special_section",
            "province_name",
            "city_name",
            "user_phone",
            "created_at",
        ]


class MyFestivalRegistrationListSerializer(serializers.ModelSerializer):
    """Serializer for my festival registrations list view"""

    province = ProvinceSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    festival_format = FestivalFormatSerializer(read_only=True)
    festival_topic = FestivalTopicSerializer(read_only=True)
    special_section = FestivalSpecialSectionSerializer(read_only=True)

    class Meta:
        model = FestivalRegistration
        fields = [
            "id",
            "full_name",
            "gender",
            "phone_number",
            "province",
            "city",
            "media_name",
            "festival_format",
            "festival_topic",
            "special_section",
            "created_at",
        ]
        read_only_fields = fields


class MyFestivalRegistrationDetailSerializer(serializers.ModelSerializer):
    """Serializer for my festival registration detail view"""

    province = ProvinceSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    festival_format = FestivalFormatSerializer(read_only=True)
    festival_topic = FestivalTopicSerializer(read_only=True)
    special_section = FestivalSpecialSectionSerializer(read_only=True)

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
        read_only_fields = fields


class WorkListSerializer(serializers.ModelSerializer):
    """Work List Serializer for listing works"""

    registration_name = serializers.CharField(
        source="festival_registration.full_name", read_only=True
    )
    media_name = serializers.CharField(
        source="festival_registration.media_name", read_only=True
    )
    festival_format = serializers.CharField(
        source="festival_registration.festival_format.name", read_only=True
    )
    festival_topic = serializers.CharField(
        source="festival_registration.festival_topic.name", read_only=True
    )
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = [
            "id",
            "title",
            "description",
            "file_url",
            "publish_link",
            "registration_name",
            "media_name",
            "festival_format",
            "festival_topic",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_file_url(self, obj):
        """Get absolute URL for file"""
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class WorkDetailSerializer(serializers.ModelSerializer):
    """Work Detail Serializer for detailed work information"""

    festival_registration = FestivalRegistrationSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    unique_filename = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = [
            "id",
            "title",
            "description",
            "file",
            "file_url",
            "file_size",
            "file_name",
            "unique_filename",
            "publish_link",
            "festival_registration",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_file_url(self, obj):
        """Get absolute URL for file"""
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_file_size(self, obj):
        """Get human readable file size"""
        if obj.file:
            try:
                size = obj.file.size
                if size < 1024:
                    return f"{size} bytes"
                elif size < 1024 * 1024:
                    return f"{size / 1024:.1f} KB"
                else:
                    return f"{size / (1024 * 1024):.1f} MB"
            except Exception:
                return None
        return None

    def get_file_name(self, obj):
        """Get display-friendly file name"""
        if obj.file:
            # Return the display name based on work title + original extension
            return obj.file_display_name
        return None

    def get_unique_filename(self, obj):
        """Get the unique filename stored in the system"""
        if obj.file:
            return obj.unique_filename
        return None


class WorkCreateSerializer(serializers.ModelSerializer):
    """Work Create/Update Serializer for creating and updating works"""

    class Meta:
        model = Work
        fields = [
            "festival_registration",
            "title",
            "description",
            "file",
            "publish_link",
        ]

    def validate_festival_registration(self, value):
        """Validate that the user owns this festival registration"""
        user = self.context["request"].user
        if value.user != user:
            raise serializers.ValidationError(
                "شما تنها می‌توانید برای ثبت نام خود اثر ایجاد کنید."
            )
        return value

    def validate_title(self, value):
        """Validate title"""
        if len(value.strip()) < 1:
            raise serializers.ValidationError("عنوان اثر باید حداقل ۳ کاراکتر باشد.")
        return value.strip()

    def validate_description(self, value):
        """Validate description"""
        if value and len(value.strip()) < 1:
            raise serializers.ValidationError("توضیحات اثر باید حداقل ۱۰ کاراکتر باشد.")
        return value.strip() if value else ""

    def validate_file(self, value):
        """Validate uploaded file"""
        if not value:
            raise serializers.ValidationError("فایل اثر الزامی است.")

        # Check file size (max 110MB)
        if value.size > 110 * 1024 * 1024:
            raise serializers.ValidationError("حجم فایل نباید بیش از ۱۱۰ مگابایت باشد.")

        # Check file extension
        allowed_extensions = [
            ".pdf",
            ".doc",
            ".docx",
            ".txt",
            ".rtf",  # Documents
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",  # Images
            ".mp4",
            ".avi",
            ".mov",
            ".mkv",
            ".wmv",  # Videos
            ".mp3",
            ".wav",
            ".aac",
            ".flac",  # Audio
            ".zip",
            ".rar",
            ".7z",  # Archives
        ]

        file_name = value.name.lower()
        if not any(file_name.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                "فرمت فایل مجاز نیست. فرمت‌های مجاز: " + ", ".join(allowed_extensions)
            )

        return value


class StatisticsSerializer(serializers.Serializer):
    """Serializer for statistics API response"""

    registered_users_count = serializers.IntegerField(
        help_text="تعداد کاربران ثبت نام شده در جشنواره"
    )
    total_works_count = serializers.IntegerField(help_text="تعداد کل اثار ارسالی")
    content_count = serializers.IntegerField(
        help_text="تعداد کل محتوا (اخبار، رویدادها، آموزش‌ها)"
    )


class MyStatisticsSerializer(serializers.Serializer):
    """Serializer for authenticated user statistics API response"""

    my_registrations_count = serializers.IntegerField(
        help_text="تعداد ثبت‌نام‌های من در جشنواره"
    )
    my_works_count = serializers.IntegerField(help_text="تعداد آثار ارسالی من")
    total_content_count = serializers.IntegerField(
        help_text="تعداد کل محتوا (اخبار، رویدادها، آموزش‌ها)"
    )
