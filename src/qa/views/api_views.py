from django.db import models
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Answer, QATag, Question
from ..serializers import (
    AnswerSerializer,
    QATagSerializer,
    QuestionCreateSerializer,
    QuestionDetailSerializer,
    QuestionListSerializer,
)


class QATagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QATag.objects.all()
    serializer_class = QATagSerializer
    lookup_field = 'slug'


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related('author', 'author__profile').prefetch_related('tags')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'create':
            return QuestionCreateSerializer
        if self.action in ('retrieve', 'update', 'partial_update'):
            return QuestionDetailSerializer
        return QuestionListSerializer

    def get_queryset(self):
        qs = Question.objects.filter(is_approved=True).select_related('author', 'author__profile').prefetch_related('tags')
        tag_slug = self.request.query_params.get('tag')
        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)
        sort = self.request.query_params.get('sort', 'recent')
        if sort == 'votes':
            qs = qs.order_by('-views_count')
        else:
            qs = qs.order_by('-created_at')
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upvote(self, request, slug=None):
        question = self.get_object()
        user = request.user
        if user in question.upvoters.all():
            question.upvoters.remove(user)
        else:
            question.upvoters.add(user)
            question.downvoters.remove(user)
        return Response({'vote_score': question.vote_score})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def downvote(self, request, slug=None):
        question = self.get_object()
        user = request.user
        if user in question.downvoters.all():
            question.downvoters.remove(user)
        else:
            question.downvoters.add(user)
            question.upvoters.remove(user)
        return Response({'vote_score': question.vote_score})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def answer(self, request, slug=None):
        question = self.get_object()
        serializer = AnswerSerializer(
            data={'question': question.id, 'content': request.data.get('content')},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, question=question)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def increment_view(self, request, slug=None):
        question = self.get_object()
        Question.objects.filter(pk=question.pk).update(views_count=models.F('views_count') + 1)
        return Response({'views_count': question.views_count + 1})


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.select_related('author', 'author__profile')
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Answer.objects.filter(is_approved=True).select_related('author', 'author__profile')
        question_slug = self.request.query_params.get('question')
        if question_slug:
            qs = qs.filter(question__slug=question_slug)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upvote(self, request, pk=None):
        answer = self.get_object()
        user = request.user
        if user in answer.upvoters.all():
            answer.upvoters.remove(user)
        else:
            answer.upvoters.add(user)
            answer.downvoters.remove(user)
        return Response({'vote_score': answer.vote_score})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def downvote(self, request, pk=None):
        answer = self.get_object()
        user = request.user
        if user in answer.downvoters.all():
            answer.downvoters.remove(user)
        else:
            answer.downvoters.add(user)
            answer.upvoters.remove(user)
        return Response({'vote_score': answer.vote_score})
