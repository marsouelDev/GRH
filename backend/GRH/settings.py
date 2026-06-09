import os
import dj_database_url
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def get_env_clean(name, default=None):
    value = os.getenv(name, default)
    if isinstance(value, str):
        return value.strip().strip("'").strip('"')
    return value

BASE_DIR = Path(__file__).resolve().parent.parent

# ═══════════════════════════════════════════════════════════════
# 1. SÉCURITÉ ET DÉBOGAGE (Dynamique pour Render)
# ═══════════════════════════════════════════════════════════════
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-j+z)jp*#n&&w80!$cz*p8@^)ru9u5uw=+cb-vh@74qa)t8yzf4')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
# Ajoute automatiquement l'URL Render (.onrender.com)
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# ═══════════════════════════════════════════════════════════════
# 2. APPLICATIONS
# ═══════════════════════════════════════════════════════════════
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Tiers
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt",
    "drf_spectacular",
    # Cloudinary pour le stockage des fichiers médias (Remplace le stockage local)
    "cloudinary",
    "cloudinary_storage",
    # Apps locales
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
    # Note: 'django_crontab' a été retiré car incompatible avec Render
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware", 
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "justification.middleware.MediaXFrameOptionsMiddleware", 
]

# ═══════════════════════════════════════════════════════════════
# 3. CONFIGURATION API & CORS
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
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    # AJOUTEZ ICI L'URL DE VOTRE FRONTEND ANGULAR EN PRODUCTION
    # "https://votre-frontend.onrender.com", 
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
# 4. BASE DE DONNÉES (PostgreSQL pour Render)
# ═══════════════════════════════════════════════════════════════
# Render ne supporte pas MySQL. Nous utilisons dj_database_url pour PostgreSQL.
# La variable DATABASE_URL sera fournie par Render ou Neon/Supabase.
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# ═══════════════════════════════════════════════════════════════
# 5. TEMPLATES, WSGI, URLS
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
# 6. FICHIERS STATIQUES & MÉDIAS (Cloudinary)
# ═══════════════════════════════════════════════════════════════
# Fichiers Statiques (CSS, JS, Images du thème)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles' # OBLIGATOIRE pour 'collectstatic' sur Render

# Fichiers Médias (Uploads utilisateurs : Justifications, Photos, etc.)
# Configuration pour Cloudinary (Stockage Cloud)
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# Limites de taille
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  

X_FRAME_OPTIONS = 'SAMEORIGIN'  

# ═══════════════════════════════════════════════════════════════
# 7. AUTHENTIFICATION & UTILISATEURS
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
# 8. EMAIL & CACHE
# ═══════════════════════════════════════════════════════════════
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Cache en mémoire (Suffisant pour commencer sur Render)
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
# 9. TÂCHES CRON (Gérées par Render Dashboard)
# ═══════════════════════════════════════════════════════════════
# La section CRONJOBS a été supprimée.
# Vous devez créer ces tâches manuellement dans le dashboard Render :
# 1. New Cron Job -> Command: python manage.py verifier_expiration_contrats --jours=7 -> Schedule: 0 8 * * *
# 2. New Cron Job -> Command: python manage.py verifier_expiration_contrats --jours=30 -> Schedule: 0 9 * * 1