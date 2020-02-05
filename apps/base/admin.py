import logging, datetime

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from solo.admin import SingletonModelAdmin
from image_cropping.admin import ImageCroppingMixin
from easy_thumbnails.fields import ThumbnailerImageField

from .models import Newsletter, PushNotification, PushNotificationConfiguration, \
    PushNotificationSchedule, UserVerificationConfiguration, \
    NewsletterLike, NewsletterComment, NewsletterCommentLike

class NewsletterModelAdmin(ImageCroppingMixin, admin.ModelAdmin):
# class NewsletterModelAdmin(admin.ModelAdmin):
    """Custom page for Newsletter"""
    # readonly_fields = ('id', 'created', 'modified', 'recommendation', 'author')
    # list_display = ('id', 'title', 'publish', 'push', 'recommendation', 'publish_date', 'refused')
    # fieldsets = (
    #     (_('Info'), {'fields': ('id', 'created', 'modified')}),
    #     (_('Options'), {'fields': ('title', 'text', 'publish', 'push',
    #                                 'publish_date', 'cropping')}),
    #     (_('Recommendation'), {'fields': ('recommendation', 'refused', 'author')}),
    # )

    def save_model(self, request, obj, form, change):

        if obj.publish == True:
            obj.publish_date = datetime.datetime.now()
        super().save_model(request, obj, form, change)
        
        if obj.push:
            obj.send_push_notification()

class NewsletterLikeModelAdmin(admin.ModelAdmin):
    """Custom page for NewsletterLike"""
    pass

class PushNotificationModelAdmin(admin.ModelAdmin):
    """Custom page for PushNotification"""
    common_fields = ('id', 'user', 'status', 'event')
    readonly_fields = common_fields + ('created', 'modified')
    list_display = readonly_fields
    list_filter = ('status', 'event')
    search_fields = ('user__phone',)

# Register your models here.
admin.site.register(Newsletter, NewsletterModelAdmin)
admin.site.register(NewsletterLike, NewsletterLikeModelAdmin)
admin.site.register(PushNotification, PushNotificationModelAdmin)
admin.site.register(PushNotificationConfiguration, SingletonModelAdmin)
admin.site.register(PushNotificationSchedule)
admin.site.register(UserVerificationConfiguration, SingletonModelAdmin)
