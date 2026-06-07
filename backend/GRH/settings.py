import os
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



SECRET_KEY = "django-insecure-j+z)jp*#n&&w80!$cz*p8@^)ru9u5uw=+cb-vh@74qa)t8yzf4"

DEBUG = True

ALLOWED_HOSTS = []


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
    "django_crontab",
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
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS":    False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN":        False,

    "TOKEN_OBTAIN_SERIALIZER": "administrateur.serializers.MyTokenObtainPairSerializer",
}

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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME":     get_env_clean("DB_NAME",     "gestion_rh_db"),
        "USER":     get_env_clean("DB_USER",     "root"),
        "PASSWORD": get_env_clean("DB_PASSWORD", "Max67172.."),
        "HOST":     get_env_clean("DB_HOST",     "127.0.0.1"),
        "PORT":     get_env_clean("DB_PORT",     "3306"),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

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


STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]


# URL publique pour accéder aux fichiers
MEDIA_URL = '/media/'

# Dossier physique où sont stockés les fichiers
MEDIA_ROOT = BASE_DIR / 'media'

# Créer le dossier automatiquement s'il n'existe pas
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(MEDIA_ROOT / 'justifications', exist_ok=True)

# Permissions des fichiers uploadés
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Taille max des fichiers (5 Mo)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  


X_FRAME_OPTIONS = 'SAMEORIGIN'  

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

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

CRONJOBS = [
    # Tous les jours à 8h
    ('0 8 * * *', 'django.core.management.call_command', ['verifier_expiration_contrats', '--jours=7']),
    # Tous les lundis à 9h (alerte plus large)
    ('0 9 * * 1', 'django.core.management.call_command', ['verifier_expiration_contrats', '--jours=30']),
]