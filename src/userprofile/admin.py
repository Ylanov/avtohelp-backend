from django.contrib import (
    admin,
    messages,
)
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from fcm_django.models import FCMDevice as BaseFCMDevice

from .models import (
    BlackList,
    FCMDevice,
    FriendList,
    FriendRequest,
    Profile,
    ProfileCar,
    ProfileGallery,
    ProfileLocation,
)

common_fields = ("id", "user", "created", "modified")


class ProfileGalleryInline(admin.TabularInline):
    """Inline for model Profile"""

    model = ProfileGallery
    classes = ["collapse"]
    extra = 1


class ProfileModelAdmin(admin.ModelAdmin):
    """Custom admin page for Profile"""

    readonly_fields = ("id", "created", "modified")
    inlines = (ProfileGalleryInline,)
    search_fields = (
        "user__phone",
        "user__profile__first_name",
        "user__profile__last_name",
        "user__profilecar__license_plate",
    )
    list_display = (
        "id",
        "user",
        "first_name",
        "last_name",
        "created",
        "modified",
    )
    fieldsets = (
        (
            _("User's data"),
            {
                "fields": (
                    "user",
                    "first_name",
                    "last_name",
                    "image",
                    "is_verified",
                )
            },
        ),
        (_("Location"), {"fields": ("city",)}),
        (_("Info"), {"fields": ("created", "modified")}),
    )


class FriendRequestModelAdmin(admin.ModelAdmin):
    """Custom admin page for FriendRequest"""

    list_display = ("id", "owner", "invited") + common_fields[-2:]


class ProfileLocationModelAdmin(admin.ModelAdmin):
    """Custom admin page for FriendRequest"""

    list_display = ("id", "user", "location") + common_fields[-2:]


class FriendListModelAdmin(admin.ModelAdmin):
    """Custom admin page for FriendList"""

    list_display = ("id", "owner", "friend", "created", "modified")


class BlackListModelAdmin(admin.ModelAdmin):
    """Custom admin page for BlackList"""

    list_display = ("id", "owner", "foe", "created", "modified")


class ProfileCarModelAdmin(admin.ModelAdmin):
    """Custom admin page for ProfileCar"""

    list_display = ("id", "owner", "car", "license_plate")


class ProfileGalleryModelAdmin(admin.ModelAdmin):
    """Custom admin page for ProfileGallery"""

    list_display = ("id", "profile", "image")


class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "device_id",
        "name",
        "type",
        "user",
        "active",
        "date_created",
    )
    list_filter = ("active",)
    actions = (
        "send_message",
        "send_bulk_message",
        "send_data_message",
        "send_bulk_data_message",
        "enable",
        "disable",
    )
    raw_id_fields = ("user",)

    if hasattr(User, "USERNAME_FIELD"):
        search_fields = (
            "name",
            "device_id",
            "user__%s" % (User.USERNAME_FIELD),
        )
    else:
        search_fields = ("name", "device_id")

    def send_messages(self, request, queryset, bulk=False, data=False):
        """
        Provides error handling for DeviceAdmin send_message and
        send_bulk_message methods.
        """
        ret = []
        errors = []
        total_failure = 0

        for device in queryset:
            if bulk:
                if data:
                    response = queryset.send_message(data={"Nick": "Mario"})
                else:
                    response = queryset.send_message(
                        title="Test notification",
                        body="Test bulk notification",
                        sound="default",
                    )
            else:
                if data:
                    response = device.send_message(data={"Nick": "Mario"})
                else:
                    response = device.send_message(
                        title="Test notification",
                        body="Test single notification",
                        sound="default",
                    )
            if response:
                ret.append(response)

            failure = int(response["failure"])
            total_failure += failure
            errors.append(str(response))

            if bulk:
                break

        if ret:
            if errors:
                msg = _("Some messages were sent: %s" % (ret))
            else:
                msg = _("All messages were sent: %s" % (ret))
            self.message_user(request, msg)

        if total_failure > 0:
            self.message_user(
                request,
                _(
                    "Some messages failed to send. %d devices were marked as "
                    "inactive." % total_failure
                ),
                level=messages.WARNING,
            )

    def send_message(self, request, queryset):
        self.send_messages(request, queryset)

    send_message.short_description = _("Send test notification")

    def send_bulk_message(self, request, queryset):
        self.send_messages(request, queryset, True)

    send_bulk_message.short_description = _("Send test notification in bulk")

    def send_data_message(self, request, queryset):
        self.send_messages(request, queryset, False, True)

    send_data_message.short_description = _("Send test data message")

    def send_bulk_data_message(self, request, queryset):
        self.send_messages(request, queryset, True, True)

    send_bulk_data_message.short_description = _(
        "Send test data message in bulk"
    )

    def enable(self, request, queryset):
        queryset.update(active=True)

    enable.short_description = _("Enable selected devices")

    def disable(self, request, queryset):
        queryset.update(active=False)

    disable.short_description = _("Disable selected devices")


# Register your models here.
admin.site.register(Profile, ProfileModelAdmin)
admin.site.register(ProfileGallery, ProfileGalleryModelAdmin)
admin.site.register(FriendRequest, FriendRequestModelAdmin)
admin.site.register(FriendList, FriendListModelAdmin)
admin.site.register(BlackList, BlackListModelAdmin)
admin.site.register(ProfileCar, ProfileCarModelAdmin)
admin.site.register(ProfileLocation, ProfileLocationModelAdmin)
admin.site.register(FCMDevice, DeviceAdmin)
#  Unregister base fcm device model
admin.site.unregister(BaseFCMDevice)
