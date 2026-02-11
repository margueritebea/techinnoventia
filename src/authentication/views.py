# authentication/views.py

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, get_user_model

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.translation import gettext_lazy as _


from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from rest_framework.decorators import api_view, permission_classes

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer, ProfileSerializer
from .tokens import set_jwt_cookies, get_tokens_for_user
from .models import Profile


########################################################################
# AUTHENTIFICATION VIA API + COOKIES JWT
########################################################################


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
        response.delete_cookie('sessionid')
        response.delete_cookie('csrftoken')
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
            "avatar": user.profile.avatar.url if hasattr(user, 'profile') and user.profile.avatar else None,

        }
    })


@api_view(["GET"])
@permission_classes([AllowAny])  # ← Changé de IsAuthenticated à AllowAny
def check_auth(request):
    # Vérifier si l'utilisateur est authentifié via JWT
    if not request.user.is_authenticated or request.user.is_anonymous:
        return Response({
            "authenticated": False
        })

    user = request.user

    return Response({
        "authenticated": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.profile.avatar.url if hasattr(user, 'profile') and user.profile.avatar else None,
        }
    })

def login_page(request):
    """
    L'authentification réelle est gérée par les endpoints API (DRF + cookies JWT).
    """
    if request.user.is_authenticated:
        return redirect("/")

    return render(request, "authentication/login.html")


def register_page(request):
    """
    L'inscription réelle est gérée par les endpoints API (DRF + cookies JWT).
    """
    if request.user.is_authenticated:
        return redirect("/")

    return render(request, "authentication/register.html")
#############################################################################################




#############################################################################################
# PROFIL UTILISATEUR
#############################################################################################

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from .models import Profile
from .serializers import UserSerializer, ProfileSerializer

User = get_user_model()


# Vue pour servir le template HTML
def profile_page(request, username=None):
    """
    Affiche la page de profil (template HTML).
    Si username est fourni, affiche le profil public.
    Sinon, affiche le profil de l'utilisateur connecté.
    """
    context = {
        'username': username,
    }
    return render(request, 'authentication/user_profile.html', context)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    GET: Récupérer le profil d'un utilisateur (public)
    PUT/PATCH: Mettre à jour son propre profil (authentifié)
    """
    serializer_class = ProfileSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'
    
    def get_queryset(self):
        return Profile.objects.select_related('user').all()
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated()]
        return []
    
    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        
        # Vérifier que l'utilisateur modifie son propre profil
        if profile.user != request.user:
            return Response(
                {"detail": "Vous ne pouvez modifier que votre propre profil."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def current_user_profile(request):
    """
    GET: Récupérer le profil de l'utilisateur connecté
    PUT/PATCH: Mettre à jour les infos utilisateur + profil
    """
    user = request.user
    profile = user.profile
    
    if request.method == 'GET':
        user_data = UserSerializer(user).data
        profile_data = ProfileSerializer(profile).data
        
        return Response({
            'user': user_data,
            'profile': profile_data
        })
    
    elif request.method in ['PUT', 'PATCH']:
        # Mise à jour des données utilisateur
        user_data = request.data.get('user', {})
        user_serializer = UserSerializer(user, data=user_data, partial=True)
        
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Mise à jour du profil
        profile_data = request.data.get('profile', {})
        profile_serializer = ProfileSerializer(profile, data=profile_data, partial=True)
        
        if profile_serializer.is_valid():
            profile_serializer.save()
            
            return Response({
                'user': user_serializer.data,
                'profile': profile_serializer.data,
                'message': 'Profil mis à jour avec succès'
            })
        else:
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """Upload avatar"""
    profile = request.user.profile
    
    if 'avatar' not in request.FILES:
        return Response(
            {"detail": "Aucun fichier fourni"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    profile.avatar = request.FILES['avatar']
    profile.save()
    
    serializer = ProfileSerializer(profile)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_cover(request):
    """Upload cover image"""
    profile = request.user.profile
    
    if 'cover_image' not in request.FILES:
        return Response(
            {"detail": "Aucun fichier fourni"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    profile.cover_image = request.FILES['cover_image']
    profile.save()
    
    serializer = ProfileSerializer(profile)
    return Response(serializer.data)


@api_view(['GET'])
def user_stats(request, username):
    """Récupérer les statistiques d'un utilisateur"""
    user = get_object_or_404(User, username=username)
    profile = user.profile
    
    return Response({
        'username': user.username,
        'reputation': profile.reputation,
        'posts_count': profile.posts_count,
        'comments_count': profile.comments_count,
        'member_since': user.date_joined,
        'is_verified': user.is_verified,
        'is_premium': user.is_premium,
    })
#############################################################################################