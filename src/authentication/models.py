# authentication/models.py
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class User(AbstractUser):
    """
    Custom user model: username + email required + quelques champs additionnels.
    """
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=150, unique=True)

    # Champs supplémentaires
    bio = models.TextField(_('bio'), max_length=500, blank=True)
    location = models.CharField(_('location'), max_length=100, blank=True)
    website = models.URLField(_('website'), blank=True)

    ROLE_CHOICES = [
        ('developer', 'Développeur'),
        ('student', 'Étudiant'),
        ('designer', 'Designer'),
        ('entrepreneur', 'Entrepreneur'),
        ('researcher', 'Chercheur'),
        ('other', 'Autre'),
    ]
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES, default='developer')

    is_verified = models.BooleanField(_('verified'), default=False)
    is_premium = models.BooleanField(_('premium'), default=False)

    date_modified = models.DateTimeField(_('date modified'), auto_now=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username


class Profile(models.Model):
    """
    Profile lié 1-1 au User.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(_('avatar'), upload_to='media/avatars/%Y/%m/%d/', blank=True, null=True)
    cover_image = models.ImageField(_('cover image'), upload_to='covers/%Y/%m/%d/', blank=True, null=True)

    # Statistiques
    reputation = models.IntegerField(_('reputation'), default=0)
    posts_count = models.IntegerField(_('posts count'), default=0)
    comments_count = models.IntegerField(_('comments count'), default=0)

    # Social links
    github = models.URLField(_('github'), blank=True)
    linkedin = models.URLField(_('linkedin'), blank=True)
    twitter = models.URLField(_('twitter'), blank=True)

    # Préférences
    email_notifications = models.BooleanField(_('email notifications'), default=True)
    newsletter = models.BooleanField(_('newsletter'), default=True)

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return f"{self.user.username}'s Profile"


User = get_user_model()


class EmailOTP(models.Model):
    """
    OTP simple pour vérification email.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_otps")
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("OTP Email")
        verbose_name_plural = _("OTP Emails")

    def is_valid(self, ttl_seconds: int = 600) -> bool:
        """Vérifie que l'OTP n'est pas expiré et pas utilisé."""
        return (timezone.now() - self.created_at).total_seconds() < ttl_seconds and not self.is_used