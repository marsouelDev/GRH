import os
import dj_database_url
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# ═══════════════════════════════════════════════════════════════
#  SÉCURITÉ ET DÉBOGAGE
# ═══════════════════════════════════════════════════════════════

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY manquante. Ajoutez-la dans les variables d'environnement Render.")

# True en local (.env), False sur Render
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# ═══════════════════════════════════════════════════════════════
#  APPLICATIONS
# ═══════════════════════════════════════════════════════════════
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt",
    "drf_spectacular",
    # Cloudinary pour le stockage des fichiers médias
    "cloudinary",
    "cloudinary_storage",
    "Users",
    "employees",
    "administrateur",
    "RH",
    "presences",
    "conges",
    "contrats",
    "justification",
    "poste",
    "rapport",
    "notification",
    "analytics",
]


# ═══════════════════════════════════════════════════════════════
#  MIDDLEWARE
# ═══════════════════════════════════════════════════════════════
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "justification.middleware.MediaXFrameOptionsMiddleware",
]


# ═══════════════════════════════════════════════════════════════
#  CONFIGURATION API & CORS
# ═══════════════════════════════════════════════════════════════
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "Users.jwt_auth.MultiModelJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

CORS_ALLOWED_ORIGINS = [
    "https://gestion-rh-lac.vercel.app",
    "http://localhost:4200",
]

CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS":    False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN":        False,
    "TOKEN_OBTAIN_SERIALIZER": "administrateur.serializers.MyTokenObtainPairSerializer",
}


# ═══════════════════════════════════════════════════════════════
#  BASE DE DONNÉES (PostgreSQL — Render)
# ═══════════════════════════════════════════════════════════════
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
    )
}


# ═══════════════════════════════════════════════════════════════
#  TEMPLATES, WSGI, URLS
# ═══════════════════════════════════════════════════════════════
ROOT_URLCONF = "GRH.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "GRH.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Douala"
USE_I18N = True
USE_TZ = True


# ═══════════════════════════════════════════════════════════════
#  FICHIERS STATIQUES & MÉDIAS
# ✅ CORRIGÉ : Utilisation du nouveau dict STORAGES (Django 5+/6)
#    DEFAULT_FILE_STORAGE et STATICFILES_STORAGE sont supprimés
#    et remplacés par STORAGES["default"] et STORAGES["staticfiles"]
# ═══════════════════════════════════════════════════════════════

# Fichiers Statiques
STATIC_URL = "static/"
_static_dir = BASE_DIR / "static"
STATICFILES_DIRS = [_static_dir] if _static_dir.exists() else []
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Fichiers Médias (uploads utilisateurs)
MEDIA_URL = '/media/'

# ✅ NOUVEAU SYSTÈME STORAGES (remplace DEFAULT_FILE_STORAGE + STATICFILES_STORAGE)
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY':    os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# Limites de taille des uploads (5 MB)
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880

X_FRAME_OPTIONS = 'SAMEORIGIN'


# ═══════════════════════════════════════════════════════════════
#  AUTHENTIFICATION & UTILISATEURS
# ═══════════════════════════════════════════════════════════════
SPECTACULAR_SETTINGS = {
    "TITLE": "API d'authentification JWT",
    "DESCRIPTION": "API avec authentification JWT utilisant DRF + Spectacular",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SECURITY": [{"BearerAuth": []}],
}

AUTH_USER_MODEL = "administrateur.Administrateur"

AUTHENTICATION_BACKENDS = [
    "Users.backends.MultiModelAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]


# ═══════════════════════════════════════════════════════════════
#  EMAIL (Brevo)
# ═══════════════════════════════════════════════════════════════
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp-relay.brevo.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# ⏱️ CRUCIAL : Timeout pour éviter que Gunicorn ne tue le worker si Brevo est lent
EMAIL_TIMEOUT = 10


# ═══════════════════════════════════════════════════════════════
#  SÉCURITÉ PRODUCTION (Activé uniquement si DEBUG = False)
# ═══════════════════════════════════════════════════════════════
if not DEBUG:
    # Force HTTPS
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Cookies sécurisés
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Protection supplémentaire
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True


# ═══════════════════════════════════════════════════════════════
#  LOGGING (Pour voir les erreurs d'email dans les logs Render)
# ═══════════════════════════════════════════════════════════════
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'RH': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'employees': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# ═══════════════════════════════════════════════════════════════
#  CACHE
# ═══════════════════════════════════════════════════════════════
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'grh-dashboard-cache',
        'TIMEOUT': 300,
        'OPTIONS': {'MAX_ENTRIES': 1000}
    }
}
CACHE_KEY_PREFIX = 'grh_'


# ═══════════════════════════════════════════════════════════════
#  TÂCHES CRON (Render Dashboard)
# ═══════════════════════════════════════════════════════════════
# Créer dans le dashboard Render → New Cron Job :
# 1. python manage.py verifier_expiration_contrats --jours=7   → Schedule: 0 8 * * *
# 2. python manage.py verifier_expiration_contrats --jours=30  → Schedule: 0 9 * * 1


# ═══════════════════════════════════════════════════════════════
#  JAZZMIN (interface admin personnalisée)
# ═══════════════════════════════════════════════════════════════
JAZZMIN_SETTINGS = {
    "site_title": "WorkFlow",
    "site_header": "Gestion des ressource humaine",
    "site_brand": "Ma Super Entreprise",
    "welcome_sign": "Bienvenue dans l'espace d'administration",
    "search_model": ["auth.User"],  # Barre de recherche globale
    "show_sidebar": True,
    "navigation_expanded": True,
}

# Pour changer les couleurs (ex: passer en mode sombre, changer le thème Bootstrap)
JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",  # Thème Bootstrap de base
    "dark_mode_theme": "darkly",
}