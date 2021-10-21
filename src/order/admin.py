from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import AssistanceRequest


class AssistanceRequestModelAdmin(admin.ModelAdmin):
    """Custom admin page for AssistanceRequest"""

    readonly_fields = ("id", "created", "modified", "status")
    list_display = ("id", "user", "status", "created", "modified")
    list_filter = ("user", "status")
    fieldsets = (
        (_("User's data"), {"fields": ("user",)}),
        (
            _("Assistance request"),
            {"fields": ("issue", "description", "status")},
        ),
        (_("Location"), {"fields": ("location",)}),
        (_("Info"), {"fields": ("created", "modified")}),
    )


# Register your models here.
admin.site.register(AssistanceRequest, AssistanceRequestModelAdmin)
