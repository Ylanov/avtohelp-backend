"""Production server configuration."""
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # NOQA

ALLOWED_HOSTS = ['avto-dobro.ru', '185.4.66.116', ]


# Integration with Sentry
sentry_sdk.init(
    dsn="https://6dca49f5f11743338eecb732e335053c@sentry.io/1467323",
    integrations=[DjangoIntegration(), CeleryIntegration()]
)


DEBUG = False
USE_CELERY = True
USE_SMS = True  # Actual sms sending switcher


# Celery settings
CELERY_RESULT_BACKEND = 'redis://localhost:6379/13'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'ORDER': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'CELERY': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    }
}
