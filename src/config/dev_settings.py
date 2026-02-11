"""
Configuration pour l'environnement de DÉVELOPPEMENT.
Hérite de base_settings.py et ajoute/surcharge les paramètres spécifiques au dev.

Utilisation via Makefile :
    make run         # Lance le serveur de dev
    make migrate     # Applique les migrations
    make migrations  # Crée les migrations
"""

from .base_settings import *

# ============================================================================
# MODE DEBUG
# ============================================================================

# DEBUG activé pour le développement - JAMAIS en production !
DEBUG = True

# ============================================================================
# CLÉS SECRÈTES
# ============================================================================
SECRET_KEY = 'django-insecure-$f&h(*z5a^rxuj3_5+qjuj2%t#wa%bfn=j152!kjx9@1j+!$7l'

# ============================================================================
# HOSTS AUTORISÉS
# ============================================================================
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

# ============================================================================
# BASE DE DONNÉES
# ============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============================================================================
# CORS (Cross-Origin Resource Sharing)
# ============================================================================

# Origines autorisées pour les requêtes AJAX
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
]

# Permet l'envoi de cookies dans les requêtes CORS
CORS_ALLOW_CREDENTIALS = True

# ============================================================================
# SÉCURITÉ DES COOKIES (Configuration HTTP, pas HTTPS)
# ============================================================================

# En développement, on n'utilise pas HTTPS, donc pas besoin de cookies sécurisés
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'  # Plus permissif qu'en production

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
# ============================================================================
# EMAIL BACKEND
# ============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ============================================================================
# LOGGING (Détaillé pour le développement)
# ============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    # Formats de log
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    
    # Handlers (où vont les logs)
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    
    # Logger racine
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    
    # Loggers spécifiques
    'loggers': {
        # Logs des sessions (utile pour déboguer l'authentification)
        'django.contrib.sessions': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        
        # Logs des requêtes SQL (mettre à DEBUG pour voir toutes les requêtes)
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',  # Changer en 'DEBUG' pour voir les requêtes SQL
            'propagate': False,
        },
        
        # Logs de votre app authentication
        'authentication': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        
        # Logs de votre app article
        'article': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        
        # Logs de votre app core
        'core': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# ============================================================================
# PARAMÈTRES OPTIONNELS DE DÉVELOPPEMENT
# ============================================================================

# Désactive la mise en cache en développement
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#     }
# }

# Permet de déboguer les templates
# TEMPLATES[0]['OPTIONS']['debug'] = True

# Pour accepter tous les hosts (NON RECOMMANDÉ, à utiliser avec prudence)
# ALLOWED_HOSTS = ['*']