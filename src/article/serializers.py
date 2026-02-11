from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework import serializers
from article.models import Article, ArticleSection, Category, Tag

User = get_user_model()

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


class ArticleSectionSerializer(serializers.ModelSerializer):
    """Serializer pour les sections d'article"""
    
    class Meta:
        model = ArticleSection
        fields = ['id', 'position', 'title', 'content', 'image', 'image_caption']
        read_only_fields = ['id']


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
    sections = ArticleSectionSerializer(many=True, required=False)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    read_time = serializers.ReadOnlyField()
    
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
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'author_name']
    
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
            return obj.is_liked_by(user)
        return False