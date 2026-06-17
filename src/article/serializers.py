import base64
import uuid

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from core.utils.markdown import render_markdown
from article.models import Article, ArticleSection, Category, Comment, Tag

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """
    Accepte soit un fichier uploadé (multipart), soit une Data URL base64
    (ex: "data:image/jpeg;base64,/9j/4AAQ...").
    Cela permet au frontend d'envoyer les images en JSON sans changer l'API.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:'):
            try:
                header, encoded = data.split(';base64,', 1)
                ext = header.split('/')[-1].split('+')[0]  # ex: "jpeg", "png", "svg"
                if ext == 'svg':
                    ext = 'svg'
                file_data = base64.b64decode(encoded)
                file_name = f'{uuid.uuid4().hex}.{ext}'
                data = ContentFile(file_data, name=file_name)
            except Exception:
                raise serializers.ValidationError('Image base64 invalide.')
        return super().to_internal_value(data)

class ArticleSectionSerializer(serializers.ModelSerializer):
    """Serializer pour les sections d'article"""
    image = Base64ImageField(required=False, allow_null=True)
    content_html = serializers.SerializerMethodField()

    class Meta:
        model = ArticleSection
        fields = ['id', 'position', 'title', 'content', 'content_html', 'image', 'image_caption']
        read_only_fields = ['id']

    def get_content_html(self, obj):
        return render_markdown(obj.content)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class ArticleListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des articles (version légère)"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    read_time = serializers.ReadOnlyField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'cover',
            'status', 'is_trending', 'author_name', 'category_name',
            'likes_count', 'comments_count', 'read_time',
            'created_at', 'updated_at', 'published_at'
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour un article avec ses sections"""
    cover = Base64ImageField(required=False, allow_null=True)
    sections = ArticleSectionSerializer(many=True, required=False)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    read_time = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    # Champs pour l'écriture
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',
        write_only=True,
        many=True,
        required=False
    )

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'cover',
            'status', 'is_trending', 'published_at',
            'category', 'category_id', 'tags', 'tag_ids',
            'sections', 'author_name',
            'likes_count', 'comments_count', 'read_time',
            'is_liked',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'author_name']

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user in obj.likes.all()
        return False

    def create(self, validated_data):
        """Création d'un article avec ses sections"""
        sections_data = validated_data.pop('sections', [])
        tags_data = validated_data.pop('tags', [])

        # Créer l'article
        article = Article.objects.create(**validated_data)

        # Ajouter les tags
        if tags_data:
            article.tags.set(tags_data)

        # Créer les sections
        for section_data in sections_data:
            ArticleSection.objects.create(article=article, **section_data)

        return article

    def update(self, instance, validated_data):
        """Mise à jour d'un article avec ses sections"""
        sections_data = validated_data.pop('sections', None)
        tags_data = validated_data.pop('tags', None)

        # Mettre à jour l'article
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Mettre à jour les tags
        if tags_data is not None:
            instance.tags.set(tags_data)

        # Mettre à jour les sections
        if sections_data is not None:
            # Récupérer les IDs des sections existantes dans les données
            section_ids = [s.get('id') for s in sections_data if s.get('id')]

            # Supprimer les sections qui ne sont plus dans la liste
            instance.sections.exclude(id__in=section_ids).delete()

            # Créer ou mettre à jour les sections
            for section_data in sections_data:
                section_id = section_data.get('id')
                if section_id:
                    # Mise à jour
                    ArticleSection.objects.filter(id=section_id, article=instance).update(**section_data)
                else:
                    # Création
                    ArticleSection.objects.create(article=instance, **section_data)

        return instance


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    likes_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()
    content_html = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    article = serializers.SlugRelatedField(slug_field='slug', queryset=Article.objects.all(), required=False)

    class Meta:
        model = Comment
        fields = [
            'id', 'article', 'author', 'author_name', 'author_username', 'author_avatar',
            'parent', 'content', 'content_html', 'is_edited', 'created_at', 'updated_at',
            'likes_count', 'is_liked', 'replies'
        ]
        read_only_fields = ['id', 'author', 'is_edited', 'created_at', 'updated_at']

    def get_content_html(self, obj):
        return render_markdown(obj.content)

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username

    def get_author_avatar(self, obj):
        try:
            if obj.author.profile.avatar:
                return obj.author.profile.avatar.url
        except Exception:
            pass
        return None

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_replies(self, obj):
        if obj.parent is not None:
            return []
        replies = obj.get_replies()
        return CommentSerializer(replies, many=True, context=self.context).data


class ArticleLikeSerializer(serializers.ModelSerializer):
    """Serializer pour renvoyer l'état mis à jour après un like"""
    likes_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'likes_count', 'is_liked']

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user in obj.likes.all()
        return False
