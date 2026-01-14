
# authentication/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crée automatiquement le profile lors de la création d'un User.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Sauvegarde le profile associé si il existe (préserve les modifications).
    """
    try:
        if hasattr(instance, "profile"):
            instance.profile.save()
    except Exception:
        # On ne veut pas interrompre la requête pour un problème de profile
        pass
