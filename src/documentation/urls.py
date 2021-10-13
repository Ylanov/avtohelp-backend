"""Documentation app current version urlconf."""
from django.urls import path

from . import views

app_name = "documentation"
urlpatterns = [
    # docs
    path("", views.RoadHelperAPIDocumentation.as_view(), name="documentation-view"),
    # schemas
    path("schema/", views.RoadHelperAPISchema.as_view(), name="doc-schema"),
]
