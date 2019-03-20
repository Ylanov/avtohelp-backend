from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _
from chat import models


# Register your models here.
class ChatRoomAdminModel(admin.ModelAdmin):
    """Admin model for ChatRoom"""
    readonly_fields = ('id', 'created', 'modified')
    list_display = readonly_fields + ('is_public',)
    filter_horizontal = ('participants',)
    fieldsets = (
        (_('Info'), {'fields': ('id', 'created', 'modified')}),
        (_('Room\'s data'), {'fields': ('name', 'participants', 'moderator', 'is_public')}),
    )

    def save_model(self, request, obj, form, change):
        """Override save action"""
        # Private chat
        if not form.data.get('moderator') and not form.data.get('is_public') and not form.data.get('name') and int(form.data.get('participants')) == 2:
            super().save_model(request, obj, form, change)

        if form.data.get('moderator') and not form.data.get('is_public') and not form.data.get('name') and int(form.data.get('participants')) == 2:
            messages.error(request, _('Private room can not have moderator.'))

        if form.data.get('is_public') and not form.data.get('name') and int(form.data.get('participants')) == 2:
            messages.error(request, _('Private room can not be public.'))

        if not form.data.get('is_public') and form.data.get('name') and int(form.data.get('participants')) == 2:
            messages.error(request, _('Private room can not have room name.'))

        if not form.data.get('is_public') and not form.data.get('name') and (int(form.data.get('participants')) > 2 or
                                                                             int(form.data.get('participants')) < 2):
            messages.error(request, _('Private room can not contain more or less than two users.'))

        # Public chat
        if form.data.get('moderator') and form.data.get('is_public') and form.data.get('name'):
            super().save_model(request, obj, form, change)

        if not form.data.get('moderator') and form.data.get('is_public') and form.data.get('name'):
            messages.error(request, _('Public room must have a moderator.'))

        if form.data.get('moderator') and not form.data.get('is_public') and form.data.get('name'):
            messages.error(request, _('Public room can not have correct flag.'))

        if form.data.get('moderator') and form.data.get('is_public') and not form.data.get('name'):
            messages.error(request, _('Public room can contain room name'))


admin.site.register(models.ChatRoom, ChatRoomAdminModel)
