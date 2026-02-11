from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class IaChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ia_chat'
    verbose_name = _('AI Chat')
    
    def ready(self):
        """Import signals when app is ready"""
        import ia_chat.signals  # noqa


