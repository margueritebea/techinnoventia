from django.urls import path

from . import views

app_name = "ia_chat"

urlpatterns = [
    path('', views.chat_page, name='chat'),
    # Conversations
    path('conversations/', views.ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:conversation_pk>/messages/', views.MessageListView.as_view(), name='message-list'),

    # User preferences
    path('preferences/', views.ConversationPreferenceView.as_view(), name='preferences'),

    # Available models
    path('models/', views.AvailableModelsView.as_view(), name='models'),
]
