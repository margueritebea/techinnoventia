# authentication/authentication.py
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CookieJWTAuthentication(JWTAuthentication):
    """
    Authentification JWT via cookies uniquement.
    Ignore complètement l'en-tête Authorization (AUTH_HEADER_TYPES peut être vide).
    """

    def authenticate(self, request):
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT.get('AUTH_COOKIE', 'access_token'))

        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except Exception:
            raise AuthenticationFailed(_("Token d'accès invalide ou expiré."))

        user = self.get_user(validated_token)
        if user is None:
            raise AuthenticationFailed(_("Utilisateur introuvable."))

        return (user, validated_token)

    def authenticate_header(self, request):
        # empêche DRF d'ajouter un header WWW-Authenticate lorsque AUTH_HEADER_TYPES est vide
        return ""
