"""
Configuration de base Django - Paramètres communs à tous les environnements.
Ce fichier contient les configurations qui ne changent pas entre dev et prod.

Utilisé comme base par :
- config.dev_settings (développement)
- config.settings (production)
"""

from pathlib import Path
from datetime import timedelta

# Chemins de base du projet
# BASE_DIR pointe vers le dossier 'src/' (là où se trouve manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent
print(f"BASE_DIR is set to: {BASE_DIR}")
# ============================================================================
# APPLICATIONS
# ============================================================================

# Applications Django par défaut
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Applications tierces (third-party packages)
THIRD_PARTY_APPS = [
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
]

# Applications personnalisées du projet
USER_APPS = [
    'core',
    'authentication',
    'article',
]

# Assemblage de toutes les applications
INSTALLED_APPS += THIRD_PARTY_APPS + USER_APPS

# ============================================================================
# MIDDLEWARE
# ============================================================================

# Ordre important pour le bon fonctionnement de Django
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS doit être avant CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'authentication.middleware.JWTAuthenticationMiddleware',  # Middleware JWT personnalisé
]

# ============================================================================
# URLS & WSGI
# ============================================================================

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# ============================================================================
# TEMPLATES
# ============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ============================================================================
# VALIDATION DES MOTS DE PASSE
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================================================
# INTERNATIONALISATION
# ============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================================================
# FICHIERS STATIQUES (CSS, JavaScript, Images)
# ============================================================================

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Utilisé par 'collectstatic' en production

# ============================================================================
# FICHIERS MÉDIA (Uploads utilisateurs)
# ============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================================
# MODÈLE & AUTHENTIFICATION
# ============================================================================

# Type de clé primaire par défaut pour les nouveaux modèles
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modèle utilisateur personnalisé
AUTH_USER_MODEL = 'authentication.User'

# Backends d'authentification
AUTHENTICATION_BACKENDS = [
    'authentication.backends.EmailOrUsernameBackend',  # Permet login avec email ou username
    'django.contrib.auth.backends.ModelBackend',  # Backend Django par défaut (fallback)
]

# Redirections après login/logout
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ============================================================================
# DJANGO REST FRAMEWORK
# ============================================================================

REST_FRAMEWORK = {
    # Utilise l'authentification JWT via cookies
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'authentication.authentication.CookieJWTAuthentication',
    ),
    
    # Par défaut, toutes les vues nécessitent une authentification
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Formats de réponse
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Interface navigateur pour tester l'API
    ],
}

# ============================================================================
# CONFIGURATION JWT (Simple JWT)
# ============================================================================

SIMPLE_JWT = {
    # Durée de vie des tokens
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Token d'accès valide 1 heure
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),  # Token refresh valide 30 jours
    
    # Rotation automatique des refresh tokens pour plus de sécurité
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,  # Invalide l'ancien token après rotation
    
    # Noms des cookies JWT
    'AUTH_COOKIE': 'access_token',
    'AUTH_COOKIE_REFRESH': 'refresh_token',
    
    # Configuration
    'AUTH_HEADER_TYPES': (),  # Désactive l'Authorization header (on utilise uniquement les cookies)
    'AUTH_COOKIE_HTTP_ONLY': True,  # Cookie non accessible via JavaScript (protection XSS)
}

# ============================================================================
# CONFIGURATION DES SESSIONS
# ============================================================================

SESSION_COOKIE_AGE = 1209600  # 2 semaines en secondes
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # La session persiste après fermeture du navigateur