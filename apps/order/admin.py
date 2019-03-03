from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import AssistanceRequest


class AssistanceRequestModelAdmin(admin.ModelAdmin):
    """Custom admin page for AssistanceRequest"""

    readonly_fields = ('id', 'user', 'created', 'modified')
    list_display = readonly_fields
    fieldsets = (
        (_('User\'s data'), {'fields': ('user', 'car',)}),
        (_('Assistance request'), {'fields': ('issue', 'description')}),
        (_('Location'), {'fields': ('location',)}),
        (_('Info'), {'fields': ('created', 'modified')}),
    )


# Register your models here.
admin.site.register(AssistanceRequest)
