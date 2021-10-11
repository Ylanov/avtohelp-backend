from django.urls import re_path

from versioning import views

app_name = "versioning"
urlpatterns = [
    re_path(
        r"^(?P<version_code>[0-9]{1,4}[.][0-9]{1,4}.[0-9]{1,4})$",
        views.VersionView.as_view(),
        name="version",
    ),
]
