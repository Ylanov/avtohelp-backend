from django.contrib import admin

from .models import Newsletter, PushNotification


class NewsletterModelAdmin(admin.ModelAdmin):
    """Custom page for Newsletter"""
    readonly_fields = ('id', 'created', 'modified')
    list_display = ('id', 'title', 'publish', 'publish_date')


class PushNotificationModelAdmin(admin.ModelAdmin):
    """Custom page for PushNotification"""
    common_fields = ('id', 'user', 'status', )
    readonly_fields = common_fields + ('created', 'modified')
    list_display = readonly_fields


# Register your models here.
admin.site.register(Newsletter, NewsletterModelAdmin)
admin.site.register(PushNotification, PushNotificationModelAdmin)
