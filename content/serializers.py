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
    Serializer for Education model
    """

    class Meta(BaseContentSerializer.Meta):
        model = Education


class EducationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Education list views
    """

    tags = TagListSerializerField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Education
        fields = ["id", "title", "publish_date", "tags", "image"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
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
