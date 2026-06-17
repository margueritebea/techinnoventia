# authentication/tokens.py

from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """
    Génère les tokens JWT pour un utilisateur
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def set_jwt_cookies(response, user, request):
    """
    Définit les cookies JWT dans la réponse HTTP
    """
    tokens = get_tokens_for_user(user)

    # Récupérer les settings avec des valeurs par défaut
    is_secure = not getattr(settings, 'DEBUG', True)  # False en dev, True en prod

    # Access token cookie
    response.set_cookie(
        key=settings.SIMPLE_JWT.get("AUTH_COOKIE", "access_token"),
        value=tokens['access'],
        httponly=True,
        secure=is_secure,  # False en dev (HTTP), True en prod (HTTPS)
        samesite='Lax',
        max_age=int(settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME").total_seconds()),
        path='/',
    )

    # Refresh token cookie
    response.set_cookie(
        key=settings.SIMPLE_JWT.get("AUTH_COOKIE_REFRESH", "refresh_token"),
        value=tokens['refresh'],
        httponly=True,
        secure=is_secure,  # False en dev (HTTP), True en prod (HTTPS)
        samesite='Lax',
        max_age=int(settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME").total_seconds()),
        path='/',
    )

    print("✅ Cookies définis: access_token, refresh_token\n")

    return response
