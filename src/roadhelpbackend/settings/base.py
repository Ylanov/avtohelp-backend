"""
Base settings shared by dev / prod / test.

Conventions:
- No hardcoded secrets. Every secret pulls from .env (see env_settings.py).
- DEBUG defaults to False. dev.py flips it on.
- settings are loaded from the explicit module via DJANGO_SETTINGS_MODULE
  (not via star-imports from __init__.py).
"""
from pathlib import Path

from .apps import INSTALLED_APPS  # noqa: F401
from .app_logger import LOGGING  # noqa: F401
from .env_settings import env

# --------------------------------------------------------------------------- paths
BASE_DIR = Path(__file__).resolve().parents[2]   # .../src
PROJECT_ROOT = BASE_DIR.parent                   # repo root

# --------------------------------------------------------------------------- core
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

ROOT_URLCONF = "roadhelpbackend.urls"
WSGI_APPLICATION = "roadhelpbackend.wsgi.application"
ASGI_APPLICATION = "roadhelpbackend.asgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "account.User"
LOGIN_URL = "admin:login"
LOGOUT_URL = "admin:logout"

# --------------------------------------------------------------------------- middleware
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",            # must be very early
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --------------------------------------------------------------------------- templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [PROJECT_ROOT / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --------------------------------------------------------------------------- database
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

# --------------------------------------------------------------------------- auth
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 9},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------------------------------- i18n
LANGUAGE_CODE = "ru"
TIME_ZONE = env("TIME_ZONE")
USE_I18N = env("USE_I18N")
USE_TZ = env("USE_TZ")
LOCALE_PATHS = [PROJECT_ROOT / "locale"]
LANGUAGES = [("ru", "Russian"), ("en", "English")]

# --------------------------------------------------------------------------- static / media
STATIC_URL = "/static/"
STATIC_ROOT = PROJECT_ROOT / "static"
MEDIA_URL = "/media/"
MEDIA_ROOT = PROJECT_ROOT / "media"

DATA_UPLOAD_MAX_MEMORY_SIZE = env("DATA_UPLOAD_MAX_MEMORY_SIZE")
FILE_UPLOAD_PERMISSIONS = 0o644

# --------------------------------------------------------------------------- API versioning
AVAILABLE_VERSIONS = {"future": "1.0.1", "current": "1.0.0"}

# --------------------------------------------------------------------------- DRF
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": env("PAGE_SIZE"),
    "COERCE_DECIMAL_TO_STRING": False,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_VERSION": AVAILABLE_VERSIONS["current"],
    "ALLOWED_VERSIONS": list(AVAILABLE_VERSIONS.values()),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "EXCEPTION_HANDLER": "utils.api_exceptions.roadhelper_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "RoadHelp API",
    "DESCRIPTION": "API для мобильного приложения взаимопомощи водителей",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# --------------------------------------------------------------------------- CORS
# By default: NO browser origins allowed. Android app ignores CORS. Web admin is same-origin.
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = False

# --------------------------------------------------------------------------- Thumbnails
THUMBNAIL_ALIASES = {
    "": {
        "news_small": {"size": (900, 600), "crop": True},
        "news_big": {"size": (1600, 1200), "crop": True},
        "news_large": {"size": (2400, 1800), "crop": True},
    },
}

# --------------------------------------------------------------------------- Redis (cache + channels + celery broker)
REDIS_DSN = f"redis://{env('REDIS_URL')}:{env('REDIS_PORT')}"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_DSN}/{env('REDIS_DB')}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_DSN]},
    },
}

# --------------------------------------------------------------------------- Celery
CELERY_BROKER_URL = f"{REDIS_DSN}/{env('REDIS_DB')}"
CELERY_RESULT_BACKEND = f"{REDIS_DSN}/{env('REDIS_DB')}"
USE_CELERY = env("USE_CELERY")
CELERY_TIMEZONE = env("TIME_ZONE")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# --------------------------------------------------------------------------- SMS / OTP
SMS_SERVICE = env("SMS_SERVICE")
SMS_LOGIN = env("SMS_LOGIN")
SMS_PASSWORD = env("SMS_PASSWORD")
SMS_SENDER = env("SMS_SENDER")
USE_SMS = env("USE_SMS")
TEST_SMS_CODE = env("TEST_SMS_CODE")
APPROVE_ACCOUNT = env("APPROVE_ACCOUNT")
SMS_SEND_DELAY = env("SMS_SEND_DELAY")
SMS_CODE_LENGTH = env("SMS_CODE_LENGTH")
SMS_INPUT_ATTEMPTS = env("SMS_INPUT_ATTEMPTS")
SMS_BLOCKING_PERIOD = env("SMS_BLOCKING_PERIOD")

OTP_SERVICE = env("OTP_SERVICE")
OTP_SERVER_KEY = env("OTP_SERVER_KEY")
OTP_SIGNATURE_KEY = env("OTP_SIGNATURE_KEY")

# --------------------------------------------------------------------------- FCM
# fcm-django 2.x uses firebase-admin SDK — initialization happens lazily via
# GOOGLE_APPLICATION_CREDENTIALS env var (path to service account JSON).
FCM_DJANGO_SETTINGS = {
    "DEFAULT_FIREBASE_APP": None,  # use default app
    "APP_VERBOSE_NAME": "RoadHelp FCM",
    "ONE_DEVICE_PER_USER": False,
    "DELETE_INACTIVE_DEVICES": True,
    "UPDATE_ON_DUPLICATE_REG_ID": True,
}

# --------------------------------------------------------------------------- Business rules
REQUEST_RELEVANCE = env("REQUEST_RELEVANCE")       # minutes
DEFAULT_REQUEST_RADIUS = env("DEFAULT_REQUEST_RADIUS")  # meters
NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS = env("NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS")
LIMIT_UNREAD_MESSAGES = env("LIMIT_UNREAD_MESSAGES")
MESSAGES_UPDATE_PERIOD = env("MESSAGES_UPDATE_PERIOD")
NEWSLETTER_USERPROFILE_ID = env("NEWSLETTER_USERPROFILE_ID")

# --------------------------------------------------------------------------- Rate limits
RATELIMIT_AUTH_PER_IP = env("RATELIMIT_AUTH_PER_IP")
RATELIMIT_AUTH_PER_PHONE = env("RATELIMIT_AUTH_PER_PHONE")
RATELIMIT_ENABLE = True
