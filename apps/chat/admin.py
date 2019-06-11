from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from chat import models


class ChatMessagesInlineModel(admin.TabularInline):
    """Inline model for ChatMessage"""
    model = models.ChatMessage
    readonly_fields = ('sender', 'message', 'created')
    fields = readonly_fields
    extra = 0


class ChatRoomInlineModel(admin.StackedInline):
    """Inline for model ChatRoom"""
    model = models.ChatRoom


class ChatRoomAdminModel(admin.ModelAdmin):
    """Admin model for ChatRoom"""
    inlines = (ChatMessagesInlineModel,)
    readonly_fields = ('id', 'created', 'modified')
    list_display = readonly_fields + ('is_public',)
    filter_horizontal = ('participants',)
    fieldsets = (
        (_('Info'), {'fields': ('id', 'created', 'modified')}),
        (_('Room\'s data'), {'fields': ('name', 'participants', 'is_public', 'image')}),
    )

    # def save_model(self, request, obj, form, change):
    #     """Override save action"""
    #     # Private chat
    #     if not form.data.get('is_public') and not form.data.get('name') and int(form.data.get('participants')) == 2:
    #         super().save_model(request, obj, form, change)
    #
    #     if form.data.get('is_public') and not form.data.get('name') and int(form.data.get('participants')) == 2:
    #         messages.error(request, _('Private room can not be public.'))
    #
    #     if not form.data.get('is_public') and form.data.get('name') and int(form.data.get('participants')) == 2:
    #         messages.error(request, _('Private room can not have room name.'))
    #
    #     if not form.data.get('is_public') and not form.data.get('name') and (int(form.data.get('participants')) > 2 or
    #                                                                          int(form.data.get('participants')) < 2):
    #         messages.error(request, _('Private room can not contain more or less than two users.'))
    #
    #     # Public chat
    #     if form.data.get('is_public') and form.data.get('name'):
    #         super().save_model(request, obj, form, change)
    #
    #     if not form.data.get('is_public') and form.data.get('name'):
    #         messages.error(request, _('Public room can not have correct flag.'))
    #
    #     if form.data.get('is_public') and not form.data.get('name'):
    #         messages.error(request, _('Public room can contain room name'))


class ChatMessageAdminModel(admin.ModelAdmin):
    """Admin model for ChatRoom"""
    readonly_fields = ('id', 'created', 'modified', 'get_room_link', 'get_room_id', 'message')
    list_display = readonly_fields[:-2]
    ordering = ('-timestamp', 'id')
    fieldsets = (
        (_('Info'), {'fields': ('id', 'created', 'modified')}),
        (_('Room\'s data'), {'fields': ('get_room_id', 'get_room_link')}),
        (_('Message'), {'fields': ('message',)}),
    )

    def get_room_link(self, instance):
        """Get user for list_fields"""
        url = reverse('admin:{}_{}_change'.format(instance.room._meta.app_label,
                                                  instance.room._meta.model_name),
                      args=(instance.room.id,))
        return format_html('<a href="{}">{}</a>', url, instance.room if not instance.room.name else instance.room.name)

    get_room_link.short_description = _('Link to chat room')

    def get_room_id(self, instance):
        """Get room id"""
        return instance.room.id

    get_room_id.short_description = _('Room ID')


class ChatReadMessageAdminModel(admin.ModelAdmin):
    """Admin model for ChatReadMessage"""
    # readonly_fields = ('id', 'created', 'modified',
    #                    'message', 'user', 'get_message_link',
    #                    'get_message_text')
    readonly_fields = ('id', 'created', 'modified',
                       'get_message_link', 'get_message_text')
    list_display = ('id', 'created', 'modified', 'user', 'get_message_link')
    fieldsets = (
        (_('Info'), {'fields': ('id', 'message')}),
        (_('Date\'s'), {'fields': ('created', 'modified')}),
        (_('Message\'s data'), {'fields': ('get_message_link', 'get_message_text')}),
        (_('Sender'), {'fields': ('user',)}),
    )

    def get_message_link(self, instance):
        """Get user for list_fields"""
        url = reverse('admin:{}_{}_change'.format(instance.message._meta.app_label,
                                                  instance.message._meta.model_name),
                      args=(instance.message.id,))
        return format_html('<a href="{}">{}</a>', url, instance.message)

    get_message_link.short_description = _('Link to chat message')

    def get_message_text(self, instance):
        """Get user for list_fields"""
        return instance.message.message

    get_message_text.short_description = _('Message text')


admin.site.register(models.ChatRoom, ChatRoomAdminModel)
admin.site.register(models.ChatMessage, ChatMessageAdminModel)
admin.site.register(models.ChatReadMessage, ChatReadMessageAdminModel)
