"""Production server configuration."""
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # NOQA

ALLOWED_HOSTS = [
    "avto-dobro.ru",
    "185.4.66.116",
]


# Integration with Sentry
sentry_sdk.init(
    dsn="https://6dca49f5f11743338eecb732e335053c@sentry.io/1467323",
    integrations=[DjangoIntegration(), CeleryIntegration()],
)


DEBUG = False
USE_CELERY = True
USE_SMS = True  # Actual sms sending switcher
TEST_SMS_CODE = False
REDIS_URL = "redis://localhost:6379/13"
APPROVE_ACCOUNT = "+79189383399"

OTP_SERVICE = "https://api.new-tel.net"
OTP_SERVER_KEY = "317c850f18a7c6b9a3e1cdcc60ba0d3c6c1e6133ce836312"
OTP_SIGNATURE_KEY = "247c41f5e06bc112745ede424861bab6e6cf678d13d76124"

NEWSLETTER_USERPROFILE_ID = 50

# CHANNELS
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    },
}


# CACHE
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
    }
}


# Celery settings
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {"level": "DEBUG", "class": "logging.StreamHandler"},
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "/code/debug.log",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "ORDER": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "CELERY": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "app": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "ACCOUNT": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
