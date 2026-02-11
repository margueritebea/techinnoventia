"""
WebSocket URL routing for ia_chat
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Chat with existing conversation
    re_path(r'ws/chat/(?P<conversation_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    
    # Start new conversation
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
]
