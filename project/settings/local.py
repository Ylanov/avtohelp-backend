"""Local settings."""
from .base import *


ALLOWED_HOSTS = (
    "localhost",
    "0.0.0.0",
    "127.0.0.1",
    "10.0.0.49",
    "ec2-3-121-42-136.eu-central-1.compute.amazonaws.com",
)


DEBUG = True
USE_CELERY = False
USE_SMS = False
TEST_SMS_CODE = True
REDIS_URL = "redis://redis:6379/1"


# CHANNELS
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("base", 6379)],
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


# Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}


# SMS
SMS_SEND_DELAY = 10
SMS_BLOCKING_PERIOD = 1


# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "null": {
            "class": "logging.NullHandler",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "/code/debug.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
        },
        "utils.messenger.connectors": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "py.warnings": {
            "handlers": ["console"],
        },
        "django.db.backends": {
            "handlers": [
                "console",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
        "app": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "CELERY": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
