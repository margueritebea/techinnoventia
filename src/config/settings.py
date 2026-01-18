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

from .base_settings import *
import os
from dotenv import load_dotenv

# ============================================================================
# CHARGEMENT DES VARIABLES D'ENVIRONNEMENT
load_dotenv()  # Charge les variables depuis un fichier .env si présent



# ============================================================================
# MODE DEBUG
# ============================================================================

# DEBUG DÉSACTIVÉ - Obligatoire en production !
# Ne JAMAIS activer DEBUG=True en production (fuite d'informations sensibles)
DEBUG = False

# ============================================================================
# CLÉS SECRÈTES
# ============================================================================

# Clé secrète depuis les variables d'environnement
# IMPORTANT : Générer une nouvelle clé unique pour la production !
# Commande : python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'CHANGE_ME_IN_PRODUCTION')

# Vérification de sécurité
if SECRET_KEY == 'CHANGE_ME_IN_PRODUCTION':
    raise ValueError("⚠️ SECRET_KEY n'est pas définie ! Définir DJANGO_SECRET_KEY dans les variables d'environnement.")

# ============================================================================
# HOSTS AUTORISÉS
# ============================================================================

# Liste des domaines autorisés à accéder à l'application
# ⚠️ IMPORTANT : Remplacer par vos vrais domaines de production
ALLOWED_HOSTS = [
    'drbea224.pythonanywhere.com',
    'votre-domaine.com',
    'www.votre-domaine.com',
]

# Récupération depuis variable d'environnement (optionnel)
# ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# ============================================================================
# BASE DE DONNÉES
# ============================================================================

# PostgreSQL recommandé pour la production (performances et fiabilité)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME'),
#         'USER': os.environ.get('DB_USER'),
#         'PASSWORD': os.environ.get('DB_PASSWORD'),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': int(os.environ.get('DB_PORT', 5432)),
        
#         # Options de performance
#         'CONN_MAX_AGE': 600,  # Garde les connexions ouvertes 10 minutes (pooling)
#         'OPTIONS': {
#             'connect_timeout': 10,  # Timeout de connexion
#         },
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Alternative : SQLite en production
# ⚠️ NON RECOMMANDÉ pour sites avec trafic important ou multiples workers
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# ============================================================================
# CORS (Cross-Origin Resource Sharing)
# ============================================================================

# Origines autorisées pour les requêtes AJAX en production
# ⚠️ Restreindre aux domaines de votre frontend uniquement
CORS_ALLOWED_ORIGINS = [
    'https://votre-domaine.com',
    'https://www.votre-domaine.com',
    'https://app.votre-domaine.com',  # Si sous-domaine pour le frontend
]

# Permet l'envoi de cookies avec les requêtes CORS
CORS_ALLOW_CREDENTIALS = True

# ============================================================================
# SÉCURITÉ DES COOKIES (Nécessite HTTPS !)
# ============================================================================

# Cookies de session - HTTPS uniquement
SESSION_COOKIE_SECURE = True  # Cookie envoyé uniquement via HTTPS
SESSION_COOKIE_SAMESITE = 'None'  # Nécessaire pour les requêtes cross-origin
SESSION_COOKIE_HTTPONLY = True  # Protection XSS (non accessible en JavaScript)

# Cookies CSRF - HTTPS uniquement
CSRF_COOKIE_SECURE = True  # Cookie CSRF uniquement via HTTPS
CSRF_COOKIE_SAMESITE = 'None'  # Nécessaire pour les requêtes cross-origin
CSRF_COOKIE_HTTPONLY = False  # CSRF doit être accessible en JavaScript pour les requêtes AJAX

# Domaines de confiance pour CSRF (Django 4.0+)
CSRF_TRUSTED_ORIGINS = [
    'https://votre-domaine.com',
    'https://www.votre-domaine.com',
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
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'server@votre-domaine.com')  # Pour les emails d'erreur

# Liste des administrateurs (recevront les emails d'erreur)
ADMINS = [
    ('Votre Nom', os.environ.get('ADMIN_EMAIL', 'admin@votre-domaine.com')),
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
# FICHIERS STATIQUES EN PRODUCTION
# ============================================================================

# WhiteNoise pour servir les fichiers statiques (si pas de CDN)
# MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Ou utiliser un CDN comme AWS S3, Cloudflare, etc.
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'