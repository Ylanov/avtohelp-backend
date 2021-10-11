"""Documentation app views."""
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView


class RedDocMixin(TemplateView):
    """Redoc Documentation view."""

    template_name = "roadhelper/reddoc.html"
    title = None
    schema_url = None

    def get_context_data(self, **kwargs):
        """Update context data."""
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["schema_url"] = self.schema_url
        return context


class SchemaMixin(TemplateView):
    """Reach yml mixin templating."""

    title = _("RoadHelper API Documentation")

    def get_context_data(self, **kwargs):
        """Update context data."""
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context


class RoadHelperAPISchema(SchemaMixin):
    """Origin documentation view."""

    template_name = "roadhelper/schema/roadhelper.yml"


class RoadHelperAPIDocumentation(RedDocMixin):
    """Documentation itself."""

    title = _("RoadHelper integration API Documentation")
    schema_url = reverse_lazy("documentation:doc-schema")
