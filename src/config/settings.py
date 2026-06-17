"""
Configuration pour l'environnement de PRODUCTION.
Hérite de base_settings.py et ajoute/surcharge les paramètres spécifiques à la prod.

⚠️ IMPORTANT : Utiliser des variables d'environnement pour les informations sensibles !

Utilisation :
    # Sur le serveur, définir DJANGO_SETTINGS_MODULE
    export DJANGO_SETTINGS_MODULE=config.settings

    # Ou utiliser --settings dans les commandes
    python manage.py migrate --settings=config.settings
"""

import os

import dj_database_url
from dotenv import load_dotenv

from .base_settings import *

# ============================================================================
# CHARGEMENT DES VARIABLES D'ENVIRONNEMENT
load_dotenv(BASE_DIR / '.env')

# ============================================================================
# MODE DEBUG
# ============================================================================
DEBUG = False

# ============================================================================
# CLÉS SECRÈTES
# ============================================================================
# Commande : python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'CHANGE_ME_IN_PRODUCTION')

if SECRET_KEY == 'CHANGE_ME_IN_PRODUCTION':
    raise ValueError("SECRET_KEY n'est pas définie ! Définir DJANGO_SECRET_KEY dans les variables d'environnement.")

# ============================================================================
# HOSTS AUTORISÉS
# ============================================================================

# Liste des domaines autorisés à accéder à l'application
# IMPORTANT : Remplacer par vos vrais domaines de production
ALLOWED_HOSTS = [
    'drbea224.pythonanywhere.com',
]

# ============================================================================
# BASE DE DONNÉES
# ============================================================================
_db_url = os.environ.get('DATABASE_URL')
if _db_url:
    DATABASES = {
        'default': dj_database_url.parse(
            _db_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ============================================================================
# CORS (Cross-Origin Resource Sharing)
# ============================================================================
_cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(',') if o.strip()]
CORS_ALLOW_CREDENTIALS = True

# ============================================================================
# SÉCURITÉ DES COOKIES (Nécessite HTTPS !)
# ============================================================================
SESSION_COOKIE_SECURE = True  # Cookie envoyé uniquement via HTTPS
SESSION_COOKIE_SAMESITE = 'None'  # Nécessaire pour les requêtes cross-origin
SESSION_COOKIE_HTTPONLY = True  # Protection XSS (non accessible en JavaScript)

CSRF_COOKIE_SECURE = True  # Cookie CSRF uniquement via HTTPS
CSRF_COOKIE_SAMESITE = 'None'  # Nécessaire pour les requêtes cross-origin
CSRF_COOKIE_HTTPONLY = False  # CSRF doit être accessible en JavaScript pour les requêtes AJAX

# Domaines de confiance pour CSRF (Django 4.0+)
CSRF_TRUSTED_ORIGINS = [
    'https://drbea224.pythonanywhere.com',
]

# ============================================================================
# PARAMÈTRES DE SÉCURITÉ SUPPLÉMENTAIRES
# ============================================================================

# Force HTTPS
SECURE_SSL_REDIRECT = True  # Redirige automatiquement HTTP vers HTTPS

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # Force HTTPS pendant 1 an (31536000 secondes)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Applique HSTS aux sous-domaines
SECURE_HSTS_PRELOAD = True  # Permet l'inclusion dans la liste de préchargement HSTS des navigateurs

# Proxy et sécurité
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Pour nginx, Apache, etc.
SECURE_CONTENT_TYPE_NOSNIFF = True  # Protection contre le MIME type sniffing
X_FRAME_OPTIONS = 'DENY'  # Protection contre le clickjacking (interdit iframes)

# Protection cookies supplémentaire
SECURE_BROWSER_XSS_FILTER = True  # Active le filtre XSS du navigateur

# ============================================================================
# LOGGING POUR LA PRODUCTION
# ============================================================================

# Créer le dossier logs s'il n'existe pas
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    # Formats de log
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },

    # Filtres
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',  # Seulement quand DEBUG=False
        },
    },

    # Handlers (destinations des logs)
    'handlers': {
        # Console (pour les logs en temps réel)
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },

        # Fichier pour les erreurs (avec rotation)
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django_errors.log',
            'maxBytes': 1024 * 1024 * 15,  # 15 MB par fichier
            'backupCount': 10,  # Garde 10 fichiers de backup
            'formatter': 'verbose',
        },

        # Fichier pour tous les logs (avec rotation)
        'file_all': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB par fichier
            'backupCount': 5,
            'formatter': 'verbose',
        },

        # Email aux admins pour les erreurs critiques
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
    },

    # Logger racine
    'root': {
        'handlers': ['console', 'file_all'],
        'level': 'INFO',
    },

    # Loggers spécifiques
    'loggers': {
        # Logs généraux de Django
        'django': {
            'handlers': ['console', 'file_all', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },

        # Logs des erreurs de requêtes HTTP
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },

        # Logs de sécurité
        'django.security': {
            'handlers': ['file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },

        # Vos applications
        'authentication': {
            'handlers': ['console', 'file_all'],
            'level': 'INFO',
            'propagate': False,
        },
        'article': {
            'handlers': ['console', 'file_all'],
            'level': 'INFO',
            'propagate': False,
        },
        'ia_chat': {
            'handlers': ['console', 'file_all'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================================================
# CONFIGURATION EMAIL
# ============================================================================

# Option 1 : Gmail (pour tests ou petits projets)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')  # Mot de passe d'application Gmail
# DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@votre-domaine.com')

# Option 2 : Service SMTP professionnel (SendGrid, Mailgun, AWS SES, etc.)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@votre-domaine.com')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'server@votre-domaine.com')

# Liste des administrateurs (recevront les emails d'erreur)
ADMINS = [
    ('PEVE Beavogui', os.environ.get('ADMIN_EMAIL', 'beavoguimaximeakoi@gmail.com')),
]
MANAGERS = ADMINS  # Les managers reçoivent les notifications de liens cassés (404)

# ============================================================================
# CACHE (Optionnel mais recommandé pour les performances)
# ============================================================================

# Option 1 : Redis (recommandé)
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         },
#         'KEY_PREFIX': 'tech_innoventia',  # Préfixe pour éviter les conflits
#         'TIMEOUT': 300,  # Timeout par défaut : 5 minutes
#     }
# }

# Option 2 : Memcached
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
#         'LOCATION': '127.0.0.1:11211',
#     }
# }

# ============================================================================
# FICHIERS STATIQUES EN PRODUCTION (WhiteNoise)
# ============================================================================
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# ============================================================================
# WEBSOCKET / CHANNELS (Redis en production)
# ============================================================================
_redis_url = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [_redis_url],
        },
    },
}
