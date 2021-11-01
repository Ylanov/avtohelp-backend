
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