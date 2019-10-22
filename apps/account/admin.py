from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdminModel(admin.ModelAdmin):
    """Custom admin page for User"""

    readonly_fields = ('id', 'profile', 'phone', 'created', 'modified')
    search_fields = ('phone', )
    list_display = ('id', 'profile', 'phone', 'created', 'modified')
    actions = ('block_user', )
    list_filter = ('is_active', )
    fieldsets = (
        (_('User\'s data'), {'fields': ('id', 'phone')}),
        (_('Info'), {'fields': ('created', 'modified')}),
        (_('Flags'), {'fields': ('is_active', 'is_staff')})
    )

    def block_user(self, request, queryset):
        """Action to disable users"""
        disabled_users = set()
        for user in queryset:
            # Check selected users
            if not user.is_active:
                disabled_users.add(user.phone.as_e164)
            else:
                user.is_active = False
                user.save()
            # Logout user
            if user.has_token:
                user.logout()
        selected_users = set(queryset.values_list('phone', flat=True))
        self.message_user(request=request,
                          message=_("""User\'s %s was successfully disabled.
                                       User\'s %s was already disabled.
                                    """) % (selected_users.difference(disabled_users) or 0,
                                            disabled_users or 0))

    block_user.short_description = _('Mark selected users as disabled')

# Register your models here.
admin.site.register(User, UserAdminModel)
