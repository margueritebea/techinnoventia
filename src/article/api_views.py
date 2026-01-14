from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Article
from .serializers import ArticleLikeSerializer

class ToggleLikeAPIView(APIView):
    """
    API pour Liker/Unliker un article.
    Endpoint: /api/articles/<slug>/like/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        user = request.user

        # Logique de bascule (Toggle)
        if user in article.likes.all():
            article.likes.remove(user)
            liked = False
        else:
            article.likes.add(user)
            liked = True

        # On renvoie les nouvelles données sérialisées
        # On passe le request dans le context pour que le serializer sache qui est l'user
        serializer = ArticleLikeSerializer(article, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
