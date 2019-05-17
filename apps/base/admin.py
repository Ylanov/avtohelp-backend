from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Newsletter, PushNotification, PushNotificationConfiguration, PushNotificationSchedule
from solo.admin import SingletonModelAdmin


class NewsletterModelAdmin(admin.ModelAdmin):
    """Custom page for Newsletter"""
    readonly_fields = ('id', 'created', 'modified')
    list_display = ('id', 'title', 'short_description', 'publish', 'publish_date')
    fieldsets = (
        (_('Info'), {'fields': ('id', 'created', 'modified')}),
        (_('Options'), {'fields': ('title', 'text', 'short_description',
                                   'publish', 'publish_date', 'image')}),
    )


class PushNotificationModelAdmin(admin.ModelAdmin):
    """Custom page for PushNotification"""
    common_fields = ('id', 'user', 'status', )
    readonly_fields = common_fields + ('created', 'modified')
    list_display = readonly_fields


# Register your models here.
admin.site.register(Newsletter, NewsletterModelAdmin)
admin.site.register(PushNotification, PushNotificationModelAdmin)
admin.site.register(PushNotificationConfiguration, SingletonModelAdmin)
admin.site.register(PushNotificationSchedule)