from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdminModel(admin.ModelAdmin):
    """Custom admin page for User"""

    readonly_fields = ('id', 'profile', 'phone', 'created', 'modified')
    search_fields = ('phone', )
    list_display = ('id', 'profile', 'phone', 'created', 'modified')
    fieldsets = (
        (_('User\'s data'), {'fields': ('id', 'phone')}),
        (_('Info'), {'fields': ('created', 'modified')}),
        (_('Flags'), {'fields': ('is_active', 'is_staff')})
    )


# Register your models here.
admin.site.register(User, UserAdminModel)
