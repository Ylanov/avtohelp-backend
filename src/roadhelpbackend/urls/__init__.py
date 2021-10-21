from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_swagger.views import get_swagger_view

from base.views import common as base_views

from . import current, future

api_schema_view = get_swagger_view(title="Road Helper API")
current_version = settings.AVAILABLE_VERSIONS.get("current")
future_version = settings.AVAILABLE_VERSIONS.get("future")

urlpatterns = [
    path("app", base_views.IndexView.as_view()),
    path("admin/", admin.site.urls),
    path(f"api/v{current_version}/", include(current, namespace=f"{current_version}")),
    path(f"api/v{future_version}/", include(future, namespace=f"{future_version}")),
    path("version/", include("versioning.urls")),
    path("swagger/", api_schema_view),
    path("documentation/", include("documentation.urls", namespace="documentation")),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
