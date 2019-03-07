from django.contrib import admin
from .models import User


class UserAdminModel(admin.ModelAdmin):
    """Custom admin page for User"""

    readonly_fields = ('id', 'profile', 'phone', 'created', 'modified')
    list_display = ('id', 'profile', 'phone', 'created', 'modified')


# Register your models here.
admin.site.register(User, UserAdminModel)
