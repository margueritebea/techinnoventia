from django.db import models
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Category, Topic
from ..serializers import (
    CategorySerializer,
    PostSerializer,
    TopicCreateSerializer,
    TopicDetailSerializer,
    TopicListSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.select_related('author', 'author__profile', 'category')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'create':
            return TopicCreateSerializer
        if self.action in ('retrieve', 'update', 'partial_update'):
            return TopicDetailSerializer
        return TopicListSerializer

    def get_queryset(self):
        qs = Topic.objects.filter(is_approved=True).select_related('author', 'author__profile', 'category')
        category_slug = self.request.query_params.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        sort = self.request.query_params.get('sort', 'recent')
        if sort == 'popular':
            qs = qs.order_by('-views_count')
        else:
            qs = qs.order_by('-is_pinned', '-created_at')
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reply(self, request, slug=None):
        topic = self.get_object()
        serializer = PostSerializer(
            data={'topic': topic.id, 'content': request.data.get('content')},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, topic=topic)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['post'])
    def increment_view(self, request, slug=None):
        topic = self.get_object()
        Topic.objects.filter(pk=topic.pk).update(views_count=models.F('views_count') + 1)
        return Response({'views_count': topic.views_count + 1})
