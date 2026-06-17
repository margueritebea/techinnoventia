from rest_framework import serializers

from core.utils.markdown import render_markdown
from .models import Category, Post, Topic


class CategorySerializer(serializers.ModelSerializer):
    topics_count = serializers.ReadOnlyField()
    posts_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'color', 'order', 'topics_count', 'posts_count']


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    content_html = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'topic', 'author', 'author_name', 'author_username', 'author_avatar',
            'content', 'content_html', 'is_solution', 'is_approved', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'is_approved', 'created_at', 'updated_at']

    def get_author_avatar(self, obj):
        try:
            if obj.author.profile.avatar:
                return obj.author.profile.avatar.url
        except Exception:
            pass
        return None

    def get_content_html(self, obj):
        return render_markdown(obj.content)


class TopicListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    replies_count = serializers.ReadOnlyField()
    last_post = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            'id', 'category', 'category_name', 'category_slug',
            'title', 'slug', 'author', 'author_name', 'author_username',
            'is_pinned', 'is_locked', 'views_count',
            'replies_count', 'last_post',
            'created_at', 'updated_at',
        ]

    def get_last_post(self, obj):
        post = obj.last_post
        if post:
            return {
                'id': post.id,
                'author_name': post.author.get_full_name() or post.author.username,
                'author_username': post.author.username,
                'created_at': post.created_at,
            }
        return None


class TopicDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    content_html = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            'id', 'category', 'category_name', 'category_slug',
            'title', 'slug', 'author', 'author_name', 'author_username', 'author_avatar',
            'content', 'content_html', 'is_pinned', 'is_locked', 'views_count',
            'posts',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'slug', 'views_count', 'created_at', 'updated_at']

    def get_author_avatar(self, obj):
        try:
            if obj.author.profile.avatar:
                return obj.author.profile.avatar.url
        except Exception:
            pass
        return None

    def get_content_html(self, obj):
        return render_markdown(obj.content)

    def get_posts(self, obj):
        posts = obj.posts.filter(is_approved=True)
        return PostSerializer(posts, many=True, context=self.context).data


class TopicCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['category', 'title', 'content', 'slug', 'id']
        read_only_fields = ['slug', 'id']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
