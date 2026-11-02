from rest_framework import serializers

from formbuilder.models import Answer, Form, Question, Submission


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "help_text",
            "qtype",
            "required",
            "order",
            "choices",
            "min_value",
            "max_value",
        ]
        read_only_fields = fields


class FormListSerializer(serializers.ModelSerializer):
    festival_title = serializers.CharField(source="festival.title", read_only=True, default=None)
    is_open = serializers.BooleanField(read_only=True)
    submitted = serializers.SerializerMethodField()

    class Meta:
        model = Form
        fields = [
            "id",
            "title",
            "description",
            "kind",
            "audience",
            "festival",
            "festival_title",
            "opens_at",
            "closes_at",
            "is_open",
            "is_anonymous",
            "submitted",
        ]
        read_only_fields = fields

    def get_submitted(self, obj):
        return obj.id in self.context.get("submitted_form_ids", ())


class FormDetailSerializer(FormListSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta(FormListSerializer.Meta):
        fields = FormListSerializer.Meta.fields + ["questions"]
        read_only_fields = fields


class AnswerReadSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source="question.text", read_only=True)
    qtype = serializers.CharField(source="question.qtype", read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ["question", "question_text", "qtype", "value", "file_url"]
        read_only_fields = fields

    def get_file_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url


class SubmissionReadSerializer(serializers.ModelSerializer):
    """پاسخ برای مدیر؛ اگر فرم ناشناس است هویت پاسخ‌دهنده حذف می‌شود"""

    answers = AnswerReadSerializer(many=True, read_only=True)
    user = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = ["id", "user", "user_name", "role", "work", "created_at", "answers"]
        read_only_fields = fields

    def get_user(self, obj):
        return None if obj.form.is_anonymous else obj.user_id

    def get_user_name(self, obj):
        return None if obj.form.is_anonymous else str(obj.user)

    def get_role(self, obj):
        return "judge" if hasattr(obj.user, "judge_profile") else "participant"
