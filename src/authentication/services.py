# authentication/services.py
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _


def send_verification_email(user, code):
    """
    Envoie un email de vérification simple. Tu peux améliorer avec template HTML.
    """
    subject = _("Vérification de votre adresse e-mail")
    # exemple simple: plain text. Pour HTML, on peut utiliser render_to_string
    message = _("Votre code de vérification est : ") + str(code)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)


def send_welcome_email(user):
    subject = _("Bienvenue sur notre plateforme !")
    message = _("Nous sommes ravis de vous compter parmi nous, ") + user.username
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)


def send_authentication_code_email(user, code):
    subject = _("Votre code d'authentification")
    message = _("Votre code est : ") + str(code)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
