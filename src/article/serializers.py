from rest_framework import serializers
from article.models import Article

class ArticleLikeSerializer(serializers.ModelSerializer):
    """Serializer pour renvoyer l'état mis à jour après un like"""
    likes_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'likes_count', 'is_liked']

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user in obj.likes.all()
        return False
