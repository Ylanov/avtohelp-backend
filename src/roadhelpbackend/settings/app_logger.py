LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
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
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "ACCOUNT": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
