"""
Festival Serializers
"""
from django.db import transaction
from rest_framework import serializers

from festival.models import (
    Festival,
    FestivalRegistration,
    Work,
    WorkFile,
    FestivalFormat,
    FestivalTopic,
    FestivalSpecialSection,
)
from festival.services import (
    attach_files,
    create_festival_registration,
    create_registration_for_user,
    ensure_festival_open,
    ensure_work_editable,
    get_sole_open_festival,
    validate_new_files,
)
from festival.uploads import upload_rules
from province.models import Province, City
from province.serializers import ProvinceSerializer, CitySerializer


def _absolute_url(serializer, file_field):
    if not file_field:
        return None
    request = serializer.context.get("request")
    if request:
        return request.build_absolute_uri(file_field.url)
    return file_field.url


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


# ---------------------------------------------------------------------------
# Festival
# ---------------------------------------------------------------------------


class FestivalBriefSerializer(serializers.ModelSerializer):
    """نمایش خلاصهٔ جشنواره داخل ثبت‌نام و اثر"""

    status = serializers.CharField(read_only=True)

    class Meta:
        model = Festival
        fields = ["id", "title", "slug", "status", "registration_start", "registration_end"]
        read_only_fields = fields


class FestivalListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    is_archived = serializers.BooleanField(read_only=True)
    banner = serializers.SerializerMethodField()

    class Meta:
        model = Festival
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "banner",
            "registration_start",
            "registration_end",
            "status",
            "is_open",
            "is_archived",
            "is_featured",
            "display_order",
        ]
        read_only_fields = fields

    def get_banner(self, obj):
        return _absolute_url(self, obj.banner)


class FestivalDetailSerializer(FestivalListSerializer):
    """جزئیات جشنواره + قالب/محور/بخش‌های ویژهٔ مجاز + قوانین آپلود + ثبت‌نام کاربر جاری"""

    formats = serializers.SerializerMethodField()
    topics = serializers.SerializerMethodField()
    special_sections = serializers.SerializerMethodField()
    upload_rules = serializers.SerializerMethodField()
    my_registration_id = serializers.SerializerMethodField()

    class Meta(FestivalListSerializer.Meta):
        fields = FestivalListSerializer.Meta.fields + [
            "formats",
            "topics",
            "special_sections",
            "upload_rules",
            "my_registration_id",
        ]
        read_only_fields = fields

    def get_formats(self, obj):
        return FestivalFormatSerializer(obj.allowed_formats(), many=True).data

    def get_topics(self, obj):
        return FestivalTopicSerializer(obj.allowed_topics(), many=True).data

    def get_special_sections(self, obj):
        return FestivalSpecialSectionSerializer(
            obj.allowed_special_sections(), many=True
        ).data

    def get_upload_rules(self, obj):
        return upload_rules()

    def get_my_registration_id(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        return (
            FestivalRegistration.objects.filter(user=request.user, festival=obj)
            .values_list("id", flat=True)
            .first()
        )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


class PersonalInfoValidationMixin:
    """اعتبارسنجی مشترک اطلاعات شخصی ثبت‌نام"""

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
        """Cross field validation: شهر باید متعلق به استان باشد"""
        province_id = data.get("province_id")
        city_id = data.get("city_id")

        if province_id and city_id:
            try:
                province = Province.objects.get(id=province_id)
                city = City.objects.get(id=city_id)
            except Province.DoesNotExist:
                raise serializers.ValidationError("استان انتخابی وجود ندارد")
            except City.DoesNotExist:
                raise serializers.ValidationError("شهر انتخابی وجود ندارد")

            if city.province_id != province.id:
                raise serializers.ValidationError(
                    "شهر انتخابی متعلق به استان انتخابی نیست"
                )

        return data

    @staticmethod
    def resolve_location(validated_data):
        """province_id/city_id را به آبجکت تبدیل می‌کند"""
        if "province_id" in validated_data:
            validated_data["province"] = Province.objects.get(
                id=validated_data.pop("province_id")
            )
        if "city_id" in validated_data:
            validated_data["city"] = City.objects.get(id=validated_data.pop("city_id"))
        return validated_data


class FestivalRegistrationSerializer(serializers.ModelSerializer):
    """Festival Registration Serializer"""

    festival = FestivalBriefSerializer(read_only=True)
    province = ProvinceSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    festival_format = FestivalFormatSerializer(read_only=True)
    festival_topic = FestivalTopicSerializer(read_only=True)
    special_section = FestivalSpecialSectionSerializer(read_only=True)

    class Meta:
        model = FestivalRegistration
        fields = [
            "id",
            "festival",
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


class FestivalRegistrationCreateSerializer(
    PersonalInfoValidationMixin, serializers.ModelSerializer
):
    """
    ثبت‌نام بدون احراز هویت (مسیر قدیمی `registration/`).
    `festival` اختیاری است: اگر نیاید و دقیقاً یک جشنواره باز باشد همان انتخاب می‌شود.
    قالب/محور دیگر لازم نیست؛ روی خود اثر ثبت می‌شود.
    """

    province_id = serializers.IntegerField(write_only=True)
    city_id = serializers.IntegerField(write_only=True)
    festival = serializers.PrimaryKeyRelatedField(
        queryset=Festival.objects.filter(is_active=True), required=False
    )

    # Accept code strings and convert to ForeignKey objects
    festival_format = serializers.SlugRelatedField(
        slug_field="code",
        queryset=FestivalFormat.objects.all(),
        required=False,
        allow_null=True,
    )
    festival_topic = serializers.SlugRelatedField(
        slug_field="code",
        queryset=FestivalTopic.objects.all(),
        required=False,
        allow_null=True,
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
            "festival",
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

    def validate(self, data):
        data = super().validate(data)
        festival = data.get("festival") or get_sole_open_festival()
        if festival is None:
            raise serializers.ValidationError(
                {"festival": ["جشنواره‌ای که می‌خواهید در آن ثبت‌نام کنید را مشخص کنید."]}
            )
        ensure_festival_open(festival)
        data["festival"] = festival
        return data

    def create(self, validated_data):
        """Create festival registration with user creation"""
        phone_number = validated_data["phone_number"]
        self.resolve_location(validated_data)

        registration, user_created = create_festival_registration(
            phone_number=phone_number, registration_data=validated_data
        )
        return registration


class MyRegistrationCreateSerializer(
    PersonalInfoValidationMixin, serializers.ModelSerializer
):
    """ثبت‌نام کاربر واردشده در یک جشنواره (festivals/<id>/register/): فقط اطلاعات شخصی"""

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
        ]

    def create(self, validated_data):
        self.resolve_location(validated_data)
        return create_registration_for_user(
            self.context["request"].user,
            {**validated_data, "festival": self.context["festival"]},
        )


class MyRegistrationUpdateSerializer(
    PersonalInfoValidationMixin, serializers.ModelSerializer
):
    """ویرایش اطلاعات شخصی ثبت‌نام (کد ملی و شماره تماس اصلی قفل است)"""

    province_id = serializers.IntegerField(write_only=True, required=False)
    city_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = FestivalRegistration
        fields = [
            "full_name",
            "father_name",
            "gender",
            "education",
            "virtual_number",
            "province_id",
            "city_id",
            "media_name",
        ]

    def validate(self, data):
        # اگر فقط یکی از استان/شهر عوض شد، با مقدار فعلی دیگری سنجیده شود
        if self.instance is not None:
            if "province_id" in data and "city_id" not in data:
                data["city_id"] = self.instance.city_id
            elif "city_id" in data and "province_id" not in data:
                data["province_id"] = self.instance.province_id
        return super().validate(data)

    def update(self, instance, validated_data):
        ensure_festival_open(instance.festival)
        self.resolve_location(validated_data)
        return super().update(instance, validated_data)


class FestivalRegistrationListSerializer(serializers.ModelSerializer):
    """Festival Registration List Serializer - lighter version for lists"""

    user_phone = serializers.CharField(source="user.phone", read_only=True)
    province_name = serializers.CharField(source="province.name", read_only=True)
    city_name = serializers.CharField(source="city.name", read_only=True)
    festival = FestivalBriefSerializer(read_only=True)
    festival_format = FestivalFormatSerializer(read_only=True)
    festival_topic = FestivalTopicSerializer(read_only=True)
    special_section = FestivalSpecialSectionSerializer(read_only=True)

    class Meta:
        model = FestivalRegistration
        fields = [
            "id",
            "festival",
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

    festival = FestivalBriefSerializer(read_only=True)
    province = ProvinceSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    festival_format = FestivalFormatSerializer(read_only=True)
    festival_topic = FestivalTopicSerializer(read_only=True)
    special_section = FestivalSpecialSectionSerializer(read_only=True)
    works_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = FestivalRegistration
        fields = [
            "id",
            "festival",
            "full_name",
            "gender",
            "phone_number",
            "province",
            "city",
            "media_name",
            "festival_format",
            "festival_topic",
            "special_section",
            "works_count",
            "created_at",
        ]
        read_only_fields = fields


class MyFestivalRegistrationDetailSerializer(serializers.ModelSerializer):
    """Serializer for my festival registration detail view"""

    festival = FestivalBriefSerializer(read_only=True)
    province = ProvinceSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    festival_format = FestivalFormatSerializer(read_only=True)
    festival_topic = FestivalTopicSerializer(read_only=True)
    special_section = FestivalSpecialSectionSerializer(read_only=True)

    class Meta:
        model = FestivalRegistration
        fields = [
            "id",
            "festival",
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


class MyFestivalSerializer(serializers.Serializer):
    """«جشنواره‌های من»: هر جشنواره‌ای که کاربر در آن ثبت‌نام کرده + شمار آثار"""

    registration_id = serializers.IntegerField(source="id")
    festival = FestivalListSerializer()
    works_count = serializers.IntegerField()
    submitted_works_count = serializers.IntegerField()
    registered_at = serializers.DateTimeField(source="created_at")


# ---------------------------------------------------------------------------
# Work
# ---------------------------------------------------------------------------


class WorkFileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    kind_display = serializers.CharField(source="get_kind_display", read_only=True)

    class Meta:
        model = WorkFile
        fields = ["id", "url", "original_name", "kind", "kind_display", "size", "created_at"]
        read_only_fields = fields

    def get_url(self, obj):
        return _absolute_url(self, obj.file)


class _WorkFilesMixin:
    """فایل‌های اثر و `file_url` سازگار با نسخهٔ قبل (اولین فایل)"""

    def _first_file_url(self, obj):
        first = next(iter(obj.files.all()), None)
        if first:
            return _absolute_url(self, first.file)
        # اثرهای قدیمی که هنوز منتقل نشده‌اند
        return _absolute_url(self, obj.file)


class WorkListSerializer(_WorkFilesMixin, serializers.ModelSerializer):
    """Work List Serializer for listing works"""

    registration_name = serializers.CharField(
        source="festival_registration.full_name", read_only=True
    )
    media_name = serializers.CharField(
        source="festival_registration.media_name", read_only=True
    )
    festival = FestivalBriefSerializer(
        source="festival_registration.festival", read_only=True
    )
    festival_format = serializers.CharField(
        source="festival_format.name", read_only=True, default=None
    )
    festival_format_code = serializers.CharField(
        source="festival_format.code", read_only=True, default=None
    )
    festival_topic = serializers.CharField(
        source="festival_topic.name", read_only=True, default=None
    )
    festival_topic_code = serializers.CharField(
        source="festival_topic.code", read_only=True, default=None
    )
    special_section = serializers.CharField(
        source="special_section.name", read_only=True, default=None
    )
    files = WorkFileSerializer(many=True, read_only=True)
    file_url = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Work
        fields = [
            "id",
            "festival_registration",
            "festival",
            "title",
            "description",
            "status",
            "status_display",
            "file_url",
            "files",
            "publish_link",
            "registration_name",
            "media_name",
            "festival_format",
            "festival_format_code",
            "festival_topic",
            "festival_topic_code",
            "special_section",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_file_url(self, obj):
        return self._first_file_url(obj)


class WorkDetailSerializer(_WorkFilesMixin, serializers.ModelSerializer):
    """Work Detail Serializer for detailed work information"""

    festival_registration = FestivalRegistrationSerializer(read_only=True)
    festival_format = FestivalFormatSerializer(read_only=True)
    festival_topic = FestivalTopicSerializer(read_only=True)
    special_section = FestivalSpecialSectionSerializer(read_only=True)
    files = WorkFileSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
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
            "status",
            "status_display",
            "files",
            "file_url",
            "file_size",
            "file_name",
            "unique_filename",
            "publish_link",
            "festival_format",
            "festival_topic",
            "special_section",
            "festival_registration",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_file_url(self, obj):
        return self._first_file_url(obj)

    def _first(self, obj):
        return next(iter(obj.files.all()), None)

    def get_file_size(self, obj):
        """Get human readable size of the first file"""
        first = self._first(obj)
        if not first:
            return None
        size = first.size
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size / (1024 * 1024):.1f} MB"

    def get_file_name(self, obj):
        first = self._first(obj)
        return first.original_name if first else None

    def get_unique_filename(self, obj):
        first = self._first(obj)
        return first.file.name.split("/")[-1] if first else None


class WorkCreateSerializer(serializers.ModelSerializer):
    """
    ایجاد/ویرایش اثر.

    - `files`: چند فایل (multipart: چند فیلد هم‌نام `files`). اختیاری؛ اثر بدون فایل «پیش‌نویس» است
      و فایل‌ها بعداً با `works/<id>/files/` اضافه می‌شوند.
    - `file`: تک‌فایل برای سازگاری با فرانت قدیمی. در ویرایش، فایل جدید به فایل‌های قبلی اضافه می‌شود.
    - قالب/محور/بخش ویژه با `code`. اگر نیاید از ثبت‌نام (قدیمی) گرفته می‌شود.
    """

    festival_format = serializers.SlugRelatedField(
        slug_field="code",
        queryset=FestivalFormat.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    festival_topic = serializers.SlugRelatedField(
        slug_field="code",
        queryset=FestivalTopic.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    special_section = serializers.SlugRelatedField(
        slug_field="code",
        queryset=FestivalSpecialSection.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    files = serializers.ListField(
        child=serializers.FileField(allow_empty_file=True),
        required=False,
        write_only=True,
    )
    file = serializers.FileField(required=False, write_only=True, allow_empty_file=True)

    class Meta:
        model = Work
        fields = [
            "festival_registration",
            "festival_format",
            "festival_topic",
            "special_section",
            "title",
            "description",
            "publish_link",
            "files",
            "file",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # در ویرایش، ثبت‌نام اثر عوض نمی‌شود و لازم نیست دوباره فرستاده شود
        if self.instance is not None:
            self.fields["festival_registration"].required = False

    def validate_festival_registration(self, value):
        """Validate that the user owns this festival registration"""
        user = self.context["request"].user
        if value.user != user:
            raise serializers.ValidationError(
                "شما تنها می‌توانید برای ثبت نام خود اثر ایجاد کنید."
            )
        return value

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("عنوان اثر باید حداقل ۳ کاراکتر باشد.")
        return value

    def validate_description(self, value):
        return value.strip() if value else ""

    def _collect_files(self, data):
        files = list(data.pop("files", None) or [])
        single = data.pop("file", None)
        if single is not None:
            files.append(single)
        return files

    def validate(self, data):
        creating = self.instance is None
        registration = data.get("festival_registration") or (
            self.instance.festival_registration if self.instance else None
        )

        if creating:
            ensure_festival_open(registration.festival)
        else:
            ensure_work_editable(self.instance)
            # ثبت‌نام اثر قابل تغییر نیست
            data.pop("festival_registration", None)

        # قالب/محور: از خود اثر؛ اگر نیامد از ثبت‌نام قدیمی
        current = self.instance
        fmt = data.get("festival_format") or (current.festival_format if current else None)
        topic = data.get("festival_topic") or (current.festival_topic if current else None)
        if creating:
            fmt = fmt or registration.festival_format
            topic = topic or registration.festival_topic
            if fmt is None:
                raise serializers.ValidationError(
                    {"festival_format": ["قالب اثر را انتخاب کنید."]}
                )
            if topic is None:
                raise serializers.ValidationError(
                    {"festival_topic": ["محور اثر را انتخاب کنید."]}
                )
            data["festival_format"] = fmt
            data["festival_topic"] = topic
            if "special_section" not in data and registration.special_section_id:
                data["special_section"] = registration.special_section

        festival = registration.festival
        if festival is not None:
            for field, label, allowed in (
                ("festival_format", "قالب", festival.allowed_formats()),
                ("festival_topic", "محور", festival.allowed_topics()),
                ("special_section", "بخش ویژه", festival.allowed_special_sections()),
            ):
                chosen = data.get(field)
                if chosen is not None and not allowed.filter(pk=chosen.pk).exists():
                    raise serializers.ValidationError(
                        {field: [f"{label} انتخابی در این جشنواره برگزار نمی‌شود."]}
                    )

        files = self._collect_files(data)
        validate_new_files(
            files, existing_count=current.files.count() if current else 0
        )
        self._uploaded_files = files
        return data

    @transaction.atomic
    def create(self, validated_data):
        work = Work.objects.create(**validated_data)
        attach_files(work, self._uploaded_files)
        return work

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        attach_files(instance, self._uploaded_files)
        return instance


class WorkFilesAddSerializer(serializers.Serializer):
    """افزودن یک یا چند فایل به اثر موجود (مرحلهٔ دوم آپلود)"""

    files = serializers.ListField(
        child=serializers.FileField(allow_empty_file=True), required=False
    )
    file = serializers.FileField(required=False, allow_empty_file=True)

    def validate(self, data):
        files = list(data.get("files") or [])
        if data.get("file") is not None:
            files.append(data["file"])
        if not files:
            raise serializers.ValidationError({"files": ["حداقل یک فایل ارسال کنید."]})
        work = self.context["work"]
        ensure_work_editable(work)
        validate_new_files(files, existing_count=work.files.count())
        data["uploaded_files"] = files
        return data


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
