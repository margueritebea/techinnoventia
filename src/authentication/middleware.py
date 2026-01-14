# authentication/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import get_user_model

User = get_user_model()

class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Authentification JWT UNIQUEMENT pour les vues non-admin
    et uniquement si l'utilisateur n'est pas déjà authentifié par session.
    """

    def process_request(self, request):
        # 🚫 Ne JAMAIS toucher à l’admin
        if request.path.startswith('/admin/'):
            return

        # ✅ Si Django a déjà authentifié l'utilisateur (session)
        if request.user and request.user.is_authenticated:
            return

        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return  # ne PAS forcer AnonymousUser

        try:
            validated_token = AccessToken(access_token)
            user_id = validated_token.get('user_id')

            user = User.objects.get(id=user_id)
            request.user = user
        except (TokenError, InvalidToken, User.DoesNotExist):
            request.user = AnonymousUser()
