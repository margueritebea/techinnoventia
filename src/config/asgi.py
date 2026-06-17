"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.asgi import get_asgi_application
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

import ia_chat.routing

User = get_user_model()


class JWTWebsocketAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        scope['user'] = AnonymousUser()
        cookies = {}
        for name, value in scope.get('headers', []):
            if name == b'cookie':
                for cookie in value.decode().split(';'):
                    cookie = cookie.strip()
                    if '=' in cookie:
                        k, v = cookie.split('=', 1)
                        cookies[k.strip()] = v.strip()
        access_token = cookies.get('access_token')
        if access_token:
            try:
                validated_token = AccessToken(access_token)
                user_id = validated_token.get('user_id')
                scope['user'] = await self.get_user(user_id)
            except (TokenError, InvalidToken, User.DoesNotExist):
                pass
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)


application = ProtocolTypeRouter({
    # HTTP requests
    "http": get_asgi_application(),

    # WebSocket requests
    "websocket": AllowedHostsOriginValidator(
        JWTWebsocketAuthMiddleware(
            URLRouter(
                ia_chat.routing.websocket_urlpatterns
            )
        )
    ),
})
