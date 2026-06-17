from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation, ConversationPreference
from .serializers import (
    ConversationDetailSerializer,
    ConversationListSerializer,
    ConversationPreferenceSerializer,
    MessageSerializer,
)


class ConversationListView(generics.ListAPIView):
    """List all conversations of the authenticated user."""

    serializer_class = ConversationListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Conversation.objects
            .filter(user=self.request.user)
            .prefetch_related('messages')
            .order_by('-updated_at')
        )


class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, partially update (title / model / history toggle), or delete a conversation."""

    serializer_class = ConversationDetailSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_object(self):
        conversation = get_object_or_404(Conversation, pk=self.kwargs['pk'])
        if conversation.user != self.request.user:
            raise PermissionDenied
        return conversation


class MessageListView(generics.ListAPIView):
    """
    List all messages in a conversation (read-only complement to the
    WebSocket load_history command — useful for initial page loads).
    """

    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation = get_object_or_404(
            Conversation,
            pk=self.kwargs['conversation_pk'],
            user=self.request.user,
        )
        return conversation.messages.order_by('created_at')


class ConversationPreferenceView(generics.RetrieveUpdateAPIView):
    """Get or update the current user's LLM preferences (auto-created on first access)."""

    serializer_class = ConversationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_object(self):
        preference, _ = ConversationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference


class AvailableModelsView(APIView):
    """
    Return display metadata for available LLM models.
    Reads the model registry from LLMService without loading any model.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            from .service.llm_service import LLMService
            models = [
                {
                    'key': key,
                    'name': config.name,
                    'context_size': config.context_size,
                }
                for key, config in LLMService.MODELS.items()
            ]
        except ImportError:
            # llama-cpp-python not installed (CI / dev without models)
            models = []
        return Response(models)


def chat_page(request):
    return render(request, 'ia_chat/chat.html')
