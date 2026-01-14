# authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from .utils import generate_unique_username
from .models import Profile

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length = 6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "role",
        ]
        extra_kwargs = {
            "username": {"required": False, "allow_blank": True},
        }

    def validate(self, data):

        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(_("Les mots de passe ne correspondent pas."))

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError(_("Un utilisateur avec cet email existe déjà."))

        return data

    def create(self, validated_data):

        password = validated_data.pop("password")
        validated_data.pop("password_confirm")

        # Générer un username uniquement si absent
        if not validated_data.get("username"):
            validated_data["username"] = generate_unique_username(
                validated_data.get("first_name",""),
                validated_data.get("last_name",""),
                validated_data["email"]
            )

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(help_text=_("Nom d'utilisateur ou adresse e-mail"))
    password = serializers.CharField(write_only=True, help_text=_("Mot de passe"))

    def validate(self, data):
        user = authenticate(username=data["identifier"], password=data["password"])
        if not user:
            # essayer par email (authenticate peut falloir backend custom)
            raise serializers.ValidationError(_("Identifiants invalides"))
        data["user"] = user
        return data




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "role", "bio", "location", "website",
            # "is_premium", "is_verified"
            ]



class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"
        fields = [
            "id", "user", "avatar", "cover_image",
            "reputation", "posts_count", "comments_count", 
            "github", "linkedin", "twitter",
            "email_notifications", "newsletter"
        ]

