# authentication/middleware.py
# authentication/middleware.py

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
import logging

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

# from django.utils.deprecation import MiddlewareMixin
# from django.contrib.auth.models import AnonymousUser
# from rest_framework_simplejwt.tokens import AccessToken
# from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class JWTAuthenticationMiddleware(MiddlewareMixin):
#     """
#     Authentification JWT UNIQUEMENT pour les vues non-admin
#     et uniquement si l'utilisateur n'est pas déjà authentifié par session.
#     """

#     def process_request(self, request):
#         # 🚫 Ne JAMAIS toucher à l’admin
#         if request.path.startswith('/admin/'):
#             return

#         # ✅ Si Django a déjà authentifié l'utilisateur (session)
#         if request.user and request.user.is_authenticated:
#             return

#         access_token = request.COOKIES.get('access_token')
#         if not access_token:
#             return  # ne PAS forcer AnonymousUser

#         try:
#             validated_token = AccessToken(access_token)
#             user_id = validated_token.get('user_id')

#             user = User.objects.get(id=user_id)
#             request.user = user
#         except (TokenError, InvalidToken, User.DoesNotExist):
#             request.user = AnonymousUser()
