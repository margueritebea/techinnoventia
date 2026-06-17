from rest_framework import serializers

from core.utils.markdown import render_markdown
from .models import Answer, QATag, Question


class QATagSerializer(serializers.ModelSerializer):
    class Meta:
        model = QATag
        fields = ['id', 'name', 'slug', 'description']


class AnswerSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    vote_score = serializers.ReadOnlyField()
    content_html = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = [
            'id', 'question', 'author', 'author_name', 'author_username', 'author_avatar',
            'content', 'content_html', 'is_accepted', 'is_approved', 'vote_score',
            'upvoters', 'downvoters',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'is_approved', 'vote_score', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username

    def get_author_avatar(self, obj):
        try:
            if obj.author.profile.avatar:
                return obj.author.profile.avatar.url
        except Exception:
            pass
        return None

    def get_content_html(self, obj):
        return render_markdown(obj.content)


class QuestionListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_username = serializers.CharField(source='author.username', read_only=True)
    tags = QATagSerializer(many=True, read_only=True)
    vote_score = serializers.ReadOnlyField()
    answers_count = serializers.ReadOnlyField()

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'slug', 'author', 'author_name', 'author_username',
            'tags', 'vote_score', 'answers_count', 'views_count',
            'is_resolved', 'created_at', 'updated_at',
        ]

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username


class QuestionDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    tags = QATagSerializer(many=True, read_only=True)
    vote_score = serializers.ReadOnlyField()
    answers_count = serializers.ReadOnlyField()
    content_html = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'slug', 'content', 'content_html', 'author',
            'author_name', 'author_username', 'author_avatar',
            'tags', 'vote_score', 'answers_count', 'views_count',
            'is_resolved', 'answers',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'slug', 'views_count', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username

    def get_author_avatar(self, obj):
        try:
            if obj.author.profile.avatar:
                return obj.author.profile.avatar.url
        except Exception:
            pass
        return None

    def get_content_html(self, obj):
        return render_markdown(obj.content)

    def get_answers(self, obj):
        answers = obj.answers.filter(is_approved=True)
        return AnswerSerializer(answers, many=True, context=self.context).data


class QuestionCreateSerializer(serializers.ModelSerializer):
    tag_names = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = Question
        fields = ['title', 'content', 'tag_names', 'slug', 'id']
        read_only_fields = ['slug', 'id']

    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        validated_data['author'] = self.context['request'].user
        question = super().create(validated_data)
        for name in tag_names:
            tag, _ = QATag.objects.get_or_create(name=name.strip())
            question.tags.add(tag)
        return question
