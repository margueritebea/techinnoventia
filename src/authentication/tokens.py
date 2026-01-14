# authentication/tokens.py
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.middleware import csrf


def get_tokens_for_user(user):
    """
    Renvoie refresh & access token (string).
    """
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def set_jwt_cookies(response, user, request):
    """
    Place access et refresh tokens en cookies HttpOnly.
    - secure : True en production (DEBUG=False)
    - samesite : 'Lax' en dev, 'None' en prod (pour cross-site)
    """
    tokens = get_tokens_for_user(user)

    is_development = getattr(settings, "DEBUG", False)
    is_secure = not is_development
    same_site = 'Lax' if is_development else 'None'

    cookie_params = {
        "httponly": True,
        "secure": is_secure,
        "samesite": same_site,
    }

    # Access token cookie
    response.set_cookie(
        key=settings.SIMPLE_JWT.get("AUTH_COOKIE", "access_token"),
        value=tokens["access"],
        max_age=int(settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME").total_seconds()),
        **cookie_params
    )

    # Refresh token cookie
    response.set_cookie(
        key=settings.SIMPLE_JWT.get("AUTH_COOKIE_REFRESH", "refresh_token"),
        value=tokens["refresh"],
        max_age=int(settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME").total_seconds()),
        **cookie_params
    )

    # Génère token CSRF (utile si tu utilises des formulaires)
    csrf.get_token(request)

    return response
