from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from base.views import common as base_views

from . import current, future

current_version = settings.AVAILABLE_VERSIONS.get("current")
future_version = settings.AVAILABLE_VERSIONS.get("future")


def healthcheck(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = (
    [
        path("health/", healthcheck, name="health"),
        path("app", base_views.IndexView.as_view()),
        # Dashboard lives UNDER /admin/ so the Unfold layout wraps it and
        # staff_member_required uses the admin login page.
        path("admin/dashboard/", include("dashboard.urls")),
        path("admin/", admin.site.urls),
        path(
            f"api/v{current_version}/",
            include(current, namespace=f"{current_version}"),
        ),
        path(
            f"api/v{future_version}/",
            include(future, namespace=f"{future_version}"),
        ),
        path("version/", include("versioning.urls")),
        # OpenAPI schema + interactive docs (drf-spectacular, replaces django-rest-swagger)
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
