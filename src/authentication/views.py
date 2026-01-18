# authentication/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.translation import gettext_lazy as _


from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer
from .tokens import set_jwt_cookies, get_tokens_for_user

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = get_tokens_for_user(user)
        response = Response({
            "message": _("Inscription réussie."),
            "user": UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)

        # set cookies
        set_jwt_cookies(response, user, request)
        return response


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        response = Response({
            "message": _("Connexion réussie."),
            "user": UserSerializer(user).data,
        }, status=status.HTTP_200_OK)

        set_jwt_cookies(response, user, request)
        return response




class CookieTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT.get("AUTH_COOKIE_REFRESH", "refresh_token"))
        if not refresh_token:
            return Response({"error": _("Refresh token manquant")}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            new_access = str(refresh.access_token)

            response = Response({"message": _("Token rafraîchi")}, status=status.HTTP_200_OK)
            response.set_cookie(
                key=settings.SIMPLE_JWT.get("AUTH_COOKIE", "access_token"),
                value=new_access,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax' if settings.DEBUG else 'None',
                max_age=int(settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME").total_seconds()),
            )
            return response
        except TokenError:
            return Response({"error": _("Refresh token invalide")}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": _("Déconnexion réussie.")}, status=status.HTTP_200_OK)
        # supprimer cookies
        response.delete_cookie(settings.SIMPLE_JWT.get("AUTH_COOKIE", "access_token"))
        response.delete_cookie(settings.SIMPLE_JWT.get("AUTH_COOKIE_REFRESH", "refresh_token"))
        return response



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_auth(request):

    user = request.user

    return Response({
        "authenticated": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.profile.avatar.url if user.profile.avatar else None,
        }
    })
##########################################################################333333

def login_page(request):
    """
    L'authentification réelle est gérée par les endpoints API (DRF + cookies JWT).
    """
    if request.user.is_authenticated:
        return redirect("/")

    return render(request, "authentication/signup.html")


def register_page(request):
    """
    L'inscription réelle est gérée par les endpoints API (DRF + cookies JWT).
    """
    if request.user.is_authenticated:
        return redirect("/")

    return render(request, "authentication/register.html")