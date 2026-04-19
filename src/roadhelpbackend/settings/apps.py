CONTRIB_APPS = [
    "daphne",              # before django.contrib.staticfiles for Channels runserver
    # django-unfold admin theme — MUST come before django.contrib.admin
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
]

EXTERNAL_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_gis",
    "drf_spectacular",  # OpenAPI schema (replaces abandoned django-rest-swagger)
    "corsheaders",
    "channels",
    "django_filters",
    "django_celery_beat",
    "phonenumber_field",
    "easy_thumbnails",
    "fcm_django",
    "multiselectfield",
    "solo",
]

PROJECT_APPS = [
    "dashboard.apps.DashboardConfig",   # AVTOHELP24 admin dashboard
    "authorization.apps.AuthorizationConfig",
    "account.apps.AccountConfig",
    "versioning.apps.VersioningConfig",
    "userprofile.apps.UserprofileConfig",
    "catalog.apps.CatalogConfig",
    "base.apps.BaseConfig",
    "order.apps.OrderConfig",
    "car.apps.CarConfig",
    "chat.apps.ChatConfig",
]

INSTALLED_APPS = CONTRIB_APPS + EXTERNAL_APPS + PROJECT_APPS
