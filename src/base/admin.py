import datetime

from django.conf import settings
from django.contrib import admin
from solo.admin import SingletonModelAdmin

from userprofile.models import Profile

from .models import (
    Newsletter,
    NewsletterComment,
    NewsletterLike,
    PushNotification,
    PushNotificationConfiguration,
    PushNotificationSchedule,
    UserVerificationConfiguration,
)


@admin.register(Newsletter)
class NewsletterModelAdmin(admin.ModelAdmin):
    """Custom page for Newsletter"""

    readonly_fields = (
        "id",
        "created",
        "modified",
        "recommendation",
        "author",
    )
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

    def save_model(self, request, obj, form, change):
        if obj.publish is True:
            obj.publish_date = datetime.datetime.now()

        if obj.as_admin is True:
            author_id = 1
            if settings.NEWSLETTER_USERPROFILE_ID:
                profile_id = settings.NEWSLETTER_USERPROFILE_ID
                profile = Profile.objects.filter(id=profile_id).get()
                if profile:
                    author_id = profile.user.id

            obj.author_id = author_id

        super().save_model(request, obj, form, change)

        if obj.push:
            obj.send_push_notification()


@admin.register(NewsletterLike)
class NewsletterLikeModelAdmin(admin.ModelAdmin):
    list_display = ("newsletter", "owner")


@admin.register(NewsletterComment)
class NewsletterCommentModelAdmin(admin.ModelAdmin):
    list_display = ("id", "newsletter", "author", "created")


@admin.register(PushNotification)
class PushNotificationModelAdmin(admin.ModelAdmin):
    common_fields = ("id", "user", "status", "event")
    readonly_fields = common_fields + ("created", "modified")
    list_display = readonly_fields
    list_filter = ("status", "event")
    search_fields = ("user__phone",)


# Register your models here.
admin.site.register(PushNotificationConfiguration, SingletonModelAdmin)
admin.site.register(PushNotificationSchedule)
admin.site.register(UserVerificationConfiguration, SingletonModelAdmin)
