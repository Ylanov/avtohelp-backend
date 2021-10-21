from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from . import models


class SMSCodeModelAdmin(admin.ModelAdmin):
    """Custom admin page for SMSCode"""

    readonly_fields = (
        "id",
        "user",
        "code",
        "status",
        "phone",
        "created",
        "modified",
    )
    list_display = readonly_fields
    list_filter = ("status", "created")
    fieldsets = (
        (
            _("User's data"),
            {
                "fields": (
                    "user",
                    "phone",
                )
            },
        ),
        (_("SMS data"), {"fields": ("code", "status")}),
        (_("Info"), {"fields": ("created", "modified")}),
    )


class UserLockModelAdmin(admin.ModelAdmin):
    """Custom admin page for UserLock"""

    list_display = ("id", "user", "created", "modified")


# Register your models here.
admin.site.register(models.SMSCode, SMSCodeModelAdmin)
admin.site.register(models.UserLock, UserLockModelAdmin)
