import os

import environ
from pathlib import Path

from easy_thumbnails.conf import Settings as thumbnail_settings

BASE_DIR = Path(__file__).resolve().parent
SETTINGS_FOLDER = Path(__file__)

SOURCE_FOLDER = SETTINGS_FOLDER.parents[1]
PROJECT_ROOT = SOURCE_FOLDER.parent.parent

PUBLIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "media"))

env = environ.Env(
    DEBUG=(bool, True),
    REDIS_URL=(str, "REDIS_URL"),
    REDIS_LOCATION=(str, "REDIS_LOCATION"),
    REDIS_PASSWORD=(str, "REDIS_PASSWORD"),
    REDIS_PORT=(str, "REDIS_PORT"),
    REDIS_DB=(str, "REDIS_DB"),
    CELERY_BROKER_URL=(str, "CELERY_BROKER_URL"),
    TIME_ZONE=(str, "europe/moscow"),
    USE_TZ=(bool, True),
    USE_I18N=(bool, True),
    USE_L10N=(bool, True),
    USE_CELERY=(bool, False),
    SECRET_KEY=(str, "SECRET_KEY"),
    SENTRY_DSN=(str, "SENTRY_DSN"),
    SMS_SERVICE=(str, "http://smsc.ru/sys/send.php"),
    SMS_LOGIN=(str, "ilyaarzumanyan92"),
    SMS_PASSWORD=(str, "93Damybee281"),
    SMS_SENDER=(str, "RoadHelper"),
    APPROVE_ACCOUNT=(str, "+79000000000"),
    TEST_SMS_CODE=(bool, False),
    USE_SMS=(bool, False),
    PAGE_SIZE=(int, 15),
    SMS_SEND_DELAY=(int, 60),
    SMS_CODE_LENGTH=(int, 5),
    SMS_INPUT_ATTEMPTS=(int, 2),
    SMS_BLOCKING_PERIOD=(int, 86400),
    NEWSLETTER_USERPROFILE_ID=(int, 1),
    NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS=(bool, True),
    REQUEST_RELEVANCE=(int, 30),
    DEFAULT_REQUEST_RADIUS=(int, 100000),
    FCM_SERVER_KEY=(
        str,
        "AAAAjcLTzLw:APA91bGE_GYkVBsKZs5S1NH3ZLmeaT7RA0-MT1a6NzeGNjUoP3rfULN2gP1zd2gsnpFVVbQjlm5EV9godH5RNarcAhxahpb9i4p2rKNa40TTT5JtrxraR0y3FZ6JlfE2Z1KTY-lWw9cM",  # noqa
    ),
    OTP_SERVICE=(str, "https://api.new-tel.net"),
    OTP_SERVER_KEY=(
        str,
        "f30a901fc45f7f082628a719f64d54ca486b7b3d0cf57714",
    ),
    OTP_SIGNATURE_KEY=(
        str,
        "ed839ad2c73e071886e0752a563f8e2dfafc7c1ce7f717d2",
    ),
    LIMIT_UNREAD_MESSAGES=(int, 3),
    MESSAGES_UPDATE_PERIOD=(int, 15),
    SESSION_SAVE_EVERY_REQUEST=(bool, True),
    DATA_UPLOAD_MAX_MEMORY_SIZE=(int, 104857600),
    FILE_UPLOAD_PERMISSIONS=(int, 0o644),
)

SECRET_KEY = "^t87c7f_vti$%_&dwb69kc22$bvh$-$rog9_b(9*r6^6o!^tp1"

USE_SMS = env("USE_SMS")
TEST_SMS_CODE = env("TEST_SMS_CODE")
APPROVE_ACCOUNT = env("APPROVE_ACCOUNT")

ALLOWED_HOSTS = [
    "0.0.0.0",
    "127.0.0.1",
    "localhost",
    "roadhelper.spider.ru",
]

CONTRIB_APPS = [
    "bootstrap_admin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
]

PROJECT_APPS = [
    "authorization.apps.AuthorizationConfig",
    "account.apps.AccountConfig",
    "utils.apps.UtilsConfig",
    "versioning.apps.VersioningConfig",
    "userprofile.apps.UserprofileConfig",
    "catalog.apps.CatalogConfig",
    "base.apps.BaseConfig",
    "order.apps.OrderConfig",
    "car.apps.CarConfig",
    "chat.apps.ChatConfig",
]

EXTERNAL_APPS = [
    "rest_framework",
    "rest_framework_gis",
    "rest_framework.authtoken",
    "rest_framework_swagger",
    "channels",
    "solo",
    "django_filters",
    "phonenumber_field",
    "easy_thumbnails",
    "image_cropping",
    "fcm_django",
    "easy_select2",
    "inline_actions",
    "django_object_actions",
    "multiselectfield",
    "colorful",
]

INSTALLED_APPS = CONTRIB_APPS + EXTERNAL_APPS + PROJECT_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "roadhelpbackend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            PROJECT_ROOT / "templates",
        ],
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


ASGI_APPLICATION = "roadhelpbackend.routing.application"

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "roadhelper",
        "USER": "roadhelper",
        "PASSWORD": "roadhelper",
        "HOST": "127.0.0.1",
        "PORT": 5432,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa
        "OPTIONS": {
            "min_length": 9,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa
    },
]

AUTH_USER_MODEL = "account.User"
LOGIN_URL = "admin:login"
LOGOUT_URL = "admin:logout"


LANGUAGE_CODE = "ru"
TIME_ZONE = env("TIME_ZONE")

USE_I18N = env("USE_I18N")
USE_L10N = env("USE_L10N")
USE_TZ = env("USE_TZ")

LOCALE_PATHS = (PROJECT_ROOT / "locale",)

STATIC_URL = "/static/"

MEDIA_ROOT = PROJECT_ROOT / "media/"
MEDIA_URL = "/media/"

STATIC_ROOT = PROJECT_ROOT / "static"

# STATICFILES_DIRS = (PROJECT_ROOT / "static",)

DEBUG = True

# Celery settings
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
USE_CELERY = env("USE_CELERY")

# Versioning
AVAILABLE_VERSIONS = {
    "future": "1.0.1",
    "current": "1.0.0",
}

# DjangoRestFramework settings
REST_DATE_FORMAT = "%d-%m-%Y"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",  # noqa
    "PAGE_SIZE": env("PAGE_SIZE"),
    "COERCE_DECIMAL_TO_STRING": False,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",  # noqa
    "DEFAULT_VERSION": (AVAILABLE_VERSIONS["current"],),
    "ALLOWED_VERSIONS": AVAILABLE_VERSIONS.values(),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "EXCEPTION_HANDLER": "utils.api_exceptions.roadhelper_exception_handler",
}


# Thumbnail settings
THUMBNAIL_ALIASES = {
    "": {
        "news_small": {"size": (900, 600), "crop": True},
        "news_big": {"size": (1600, 1200), "crop": True},
        "news_large": {"size": (2400, 1800), "crop": True},
    },
}

# CORS Config
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = False


# SMS
SMS_SEND_DELAY = env("SMS_SEND_DELAY")  # seconds
SMS_CODE_LENGTH = env("SMS_CODE_LENGTH")  # characters
SMS_INPUT_ATTEMPTS = env("SMS_INPUT_ATTEMPTS")  # count of attempts
SMS_BLOCKING_PERIOD = env("SMS_BLOCKING_PERIOD")  # 24 hours in seconds


NEWSLETTER_USERPROFILE_ID = env("NEWSLETTER_USERPROFILE_ID")

# CHAT
NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS = env(
    "NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS"
)


# ASSISTANCE REQUESTS
REQUEST_RELEVANCE = env("REQUEST_RELEVANCE")  # minutes
DEFAULT_REQUEST_RADIUS = env("DEFAULT_REQUEST_RADIUS")  # in meters


# PUSH-NOTIFICATIONS
# Django FCM (Firebase push notifications)
FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY": (env("FCM_SERVER_KEY")),
}


# SMSC Settings
SMS_SERVICE = env("SMS_SERVICE")
SMS_LOGIN = env("SMS_LOGIN")
SMS_PASSWORD = env("SMS_PASSWORD")
SMS_SENDER = env("SMS_SENDER")

# STORE URL FOR MOBILE APPLICATION
# set urls in file: media/static/js/device.js
# comment this lines
# STORE_APPLE = 'https://apps.apple.com/ru/app/id1419101818'
# STORE_GOOGLE = 'https://play.google.com/store/apps/details?id=ru.autohelp'

OTP_SERVICE = env("OTP_SERVICE")
OTP_SERVER_KEY = env("OTP_SERVER_KEY")
OTP_SIGNATURE_KEY = env("OTP_SIGNATURE_KEY")

# Message PUSH-notifications
LIMIT_UNREAD_MESSAGES = env("LIMIT_UNREAD_MESSAGES")
MESSAGES_UPDATE_PERIOD = env("MESSAGES_UPDATE_PERIOD")


# Save the session to the database on every single request
SESSION_SAVE_EVERY_REQUEST = env("SESSION_SAVE_EVERY_REQUEST")


# Django Rest Swagger
SWAGGER_SETTINGS = {
    "JSON_EDITOR": False,
    "SHOW_REQUEST_HEADERS": True,
    "SECURITY_DEFINITIONS": {
        "api_key": {
            "type": "apiKey",
            "description": "Token authorization",
            "name": "Authorization",
            "in": "header",
        }
    },
}


DATA_UPLOAD_MAX_MEMORY_SIZE = env("DATA_UPLOAD_MAX_MEMORY_SIZE")
FILE_UPLOAD_PERMISSIONS = env("FILE_UPLOAD_PERMISSIONS")

THUMBNAIL_PROCESSORS = (
    "image_cropping.thumbnail_processors.crop_corners",
) + thumbnail_settings.THUMBNAIL_PROCESSORS

IMAGE_CROPPING_BACKEND = (
    "image_cropping.backends.easy_thumbs.EasyThumbnailsBackend"
)
IMAGE_CROPPING_BACKEND_PARAMS = {}
