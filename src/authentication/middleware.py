# authentication/middleware.py
# authentication/middleware.py

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()
logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware:
    """
    Middleware pour authentifier l'utilisateur via JWT stocké dans les cookies.
    S'exécute APRÈS AuthenticationMiddleware de Django.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ne pas toucher aux routes admin
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        # Si déjà authentifié via session Django
        if hasattr(request, 'user') and request.user.is_authenticated:
            return self.get_response(request)

        # Essayer d'authentifier via JWT cookie
        access_token = request.COOKIES.get('access_token')

        if access_token:
            try:
                validated_token = AccessToken(access_token)
                user_id = validated_token.get('user_id')
                user = User.objects.get(id=user_id)
                request.user = user
                logger.debug(f"JWT Auth: {user.username} authenticated")
            except (TokenError, InvalidToken) as e:
                logger.warning(f"Invalid JWT token: {str(e)[:100]}")
                request.user = AnonymousUser()
            except User.DoesNotExist:
                logger.warning(f"User ID {user_id} not found")
                request.user = AnonymousUser()

        response = self.get_response(request)
        return response
