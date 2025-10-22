"""
Serializers for Content Models
Handles serialization for News, Education, and Event models
"""
from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import News, Education, Event


class BaseContentSerializer(TaggitSerializer, serializers.ModelSerializer):
    """
    Base serializer for content models with taggit support
    """

    tags = TagListSerializerField()

    class Meta:
        fields = [
            "id",
            "title",
            "description",
            "image",
            "publish_date",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class NewsSerializer(BaseContentSerializer):
    """
    Serializer for News model
    """

    class Meta(BaseContentSerializer.Meta):
        model = News


class NewsListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for News list views
    """

    tags = TagListSerializerField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = ["id", "title", "publish_date", "tags", "image"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class EducationSerializer(BaseContentSerializer):
    """
    Serializer for Education model with video and document support
    """

    video = serializers.FileField(required=False, allow_null=True)
    document = serializers.FileField(required=False, allow_null=True)

    class Meta(BaseContentSerializer.Meta):
        model = Education
        fields = BaseContentSerializer.Meta.fields + ["video", "document"]

    def validate_video(self, value):
        """Validate video file size and format"""
        if value is None:
            return value

        # Check file size (500MB max)
        max_size = 500 * 1024 * 1024  # 500MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                f"حجم فایل ویدیو نباید بیشتر از 500 مگابایت باشد. (حجم فعلی: {value.size / (1024 * 1024):.2f} مگابایت)"
            )

        # Check file extension
        allowed_extensions = [".mp4", ".avi", ".mov", ".mkv", ".wmv"]
        file_ext = value.name.lower()[value.name.rfind(".") :]
        if file_ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"فرمت فایل ویدیو مجاز نیست. فرمت‌های مجاز: {', '.join(allowed_extensions)}"
            )

        return value

    def validate_document(self, value):
        """Validate document file size and format"""
        if value is None:
            return value

        # Check file size (50MB max)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                f"حجم فایل سند نباید بیشتر از 50 مگابایت باشد. (حجم فعلی: {value.size / (1024 * 1024):.2f} مگابایت)"
            )

        # Check file extension
        allowed_extensions = [".pdf", ".ppt", ".pptx"]
        file_ext = value.name.lower()[value.name.rfind(".") :]
        if file_ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"فرمت فایل سند مجاز نیست. فرمت‌های مجاز: {', '.join(allowed_extensions)}"
            )

        return value


class EducationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Education list views with media status
    """

    tags = TagListSerializerField()
    image = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    document_url = serializers.SerializerMethodField()
    has_video = serializers.BooleanField(read_only=True)
    has_document = serializers.BooleanField(read_only=True)

    class Meta:
        model = Education
        fields = [
            "id",
            "title",
            "publish_date",
            "tags",
            "image",
            "has_video",
            "has_document",
            "video_url",
            "document_url",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_video_url(self, obj):
        """Return video URL if exists"""
        request = self.context.get("request")
        if obj.video:
            if request is not None:
                return request.build_absolute_uri(obj.video.url)
            return obj.video.url
        return None

    def get_document_url(self, obj):
        """Return document URL if exists"""
        request = self.context.get("request")
        if obj.document:
            if request is not None:
                return request.build_absolute_uri(obj.document.url)
            return obj.document.url
        return None


class EventSerializer(BaseContentSerializer):
    """
    Serializer for Event model
    """

    class Meta(BaseContentSerializer.Meta):
        model = Event


class EventListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Event list views
    """

    tags = TagListSerializerField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ["id", "title", "publish_date", "tags", "image"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
