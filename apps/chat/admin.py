from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from chat import models


# Register your models here.
class ChatRoomAdminModel(admin.ModelAdmin):
    """Admin model for ChatRoom"""
    readonly_fields = ('id', 'created', 'modified')
    list_display = readonly_fields + ('initiator', 'participant', 'is_public')
    fieldsets = (
        (_('Info'), {'fields': ('id', 'created', 'modified')}),
        (_('Room\'s data'), {'fields': ('initiator', 'participant', 'is_public')}),
    )


admin.site.register(models.ChatRoom, ChatRoomAdminModel)