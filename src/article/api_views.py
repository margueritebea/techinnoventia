from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article, Category, Comment, Tag
from .serializers import (
    ArticleDetailSerializer,
    ArticleLikeSerializer,
    ArticleListSerializer,
    CategorySerializer,
    CommentSerializer,
    TagSerializer,
)


class ToggleLikeAPIView(APIView):
    """
    API pour Liker/Unliker un article.
    Endpoint: /api/articles/<slug>/like/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        user = request.user

        if user in article.likes.all():
            article.likes.remove(user)
        else:
            article.likes.add(user)

        serializer = ArticleLikeSerializer(article, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
class IsAuthorOrReadOnly(permissions.BasePermission):
    """Permission personnalisée : seul l'auteur peut modifier"""

    def has_object_permission(self, request, view, obj):
        # Lecture autorisée pour tous
        if request.method in permissions.SAFE_METHODS:
            return True

        # Écriture autorisée uniquement pour l'auteur
        return obj.author == request.user


class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les articles

    Liste, création, modification, suppression d'articles
    """
    queryset = Article.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        """Utiliser différents serializers selon l'action"""
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleDetailSerializer

    def get_queryset(self):
        """Optimiser les requêtes et filtrer selon les permissions"""
        queryset = Article.objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'tags', 'sections', 'likes', 'comments'
        )

        # Les utilisateurs non authentifiés ne voient que les articles publiés
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='published')
        else:
            # Les utilisateurs authentifiés voient leurs propres articles + les publiés
            queryset = queryset.filter(
                models.Q(status='published') | models.Q(author=self.request.user)
            )

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Définir l'auteur lors de la création"""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def publish(self, request, slug=None):
        """
        Publier un article (passe du statut draft à published)
        POST /api/articles/{slug}/publish/
        """
        article = self.get_object()

        # Vérifier que l'utilisateur est bien l'auteur
        if article.author != request.user:
            return Response(
                {'error': 'Vous n\'êtes pas autorisé à publier cet article'},
                status=status.HTTP_403_FORBIDDEN
            )

        article.status = 'published'
        if not article.published_at:
            article.published_at = timezone.now()
        article.save()

        serializer = self.get_serializer(article)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unpublish(self, request, slug=None):
        """
        Dépublier un article (repasse en draft)
        POST /api/articles/{slug}/unpublish/
        """
        article = self.get_object()

        # Vérifier que l'utilisateur est bien l'auteur
        if article.author != request.user:
            return Response(
                {'error': 'Vous n\'êtes pas autorisé à dépublier cet article'},
                status=status.HTTP_403_FORBIDDEN
            )

        article.status = 'draft'
        article.save()

        serializer = self.get_serializer(article)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_articles(self, request):
        """
        Récupérer tous les articles de l'utilisateur connecté
        GET /api/articles/my_articles/
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentification requise'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        articles = self.get_queryset().filter(author=request.user)
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(is_approved=True).select_related('author', 'author__profile')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.filter(is_approved=True).select_related('author', 'author__profile')
        article_slug = self.request.query_params.get('article')
        if article_slug:
            queryset = queryset.filter(article__slug=article_slug)
        return queryset.filter(parent__isnull=True)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(is_edited=True)

    @action(detail=True, methods=['post'])
    def toggle_like(self, request, pk=None):
        comment = self.get_object()
        user = request.user
        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
        else:
            comment.likes.add(user)
        serializer = self.get_serializer(comment)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les catégories (lecture seule)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les tags (lecture seule)"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'
