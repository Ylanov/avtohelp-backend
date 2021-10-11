import logging, datetime

from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from solo.admin import SingletonModelAdmin
from image_cropping.admin import ImageCroppingMixin
from easy_thumbnails.fields import ThumbnailerImageField

from .models import (
    Newsletter,
    PushNotification,
    PushNotificationConfiguration,
    PushNotificationSchedule,
    UserVerificationConfiguration,
    NewsletterLike,
    NewsletterComment,
    NewsletterCommentLike,
)
from userprofile.models import Profile


class NewsletterModelAdmin(ImageCroppingMixin, admin.ModelAdmin):
    # class NewsletterModelAdmin(admin.ModelAdmin):
    """Custom page for Newsletter"""

    readonly_fields = ("id", "created", "modified", "recommendation", "author")
    list_display = (
        "id",
        "text",
        "publish",
        "push",
        "recommendation",
        "publish_date",
        "refused",
    )
    exclude = (
        "title",
        "short_description",
    )

    # def get_form(self, request, obj=None, **kwargs):
    #     if obj:
    #         if obj.recommendation != None and obj.recommendation == False:
    #             self.exclude = ('title', 'short_description', 'refused', )
    #     form = super().get_form(request, obj, **kwargs)
    #     return form

    def save_model(self, request, obj, form, change):
        if obj.publish == True:
            obj.publish_date = datetime.datetime.now()

        if obj.as_admin == True:
            author_id = 1
            if settings.NEWSLETTER_USERPROFILE_ID:
                profile_id = settings.NEWSLETTER_USERPROFILE_ID
                profile = Profile.objects.filter(id=profile_id).get()
                if profile:
                    author_id = profile.user.id
            author = obj.author_id = author_id
        super().save_model(request, obj, form, change)

        if obj.push:
            obj.send_push_notification()


class NewsletterLikeModelAdmin(admin.ModelAdmin):
    """Custom page for NewsletterLike"""

    pass


class NewsletterCommentModelAdmin(admin.ModelAdmin):
    """Custom page for NewsletterLike"""

    pass


class PushNotificationModelAdmin(admin.ModelAdmin):
    """Custom page for PushNotification"""

    common_fields = ("id", "user", "status", "event")
    readonly_fields = common_fields + ("created", "modified")
    list_display = readonly_fields
    list_filter = ("status", "event")
    search_fields = ("user__phone",)


# Register your models here.
admin.site.register(Newsletter, NewsletterModelAdmin)
admin.site.register(NewsletterLike, NewsletterLikeModelAdmin)
admin.site.register(NewsletterComment, NewsletterCommentModelAdmin)
admin.site.register(PushNotification, PushNotificationModelAdmin)
admin.site.register(PushNotificationConfiguration, SingletonModelAdmin)
admin.site.register(PushNotificationSchedule)
admin.site.register(UserVerificationConfiguration, SingletonModelAdmin)
