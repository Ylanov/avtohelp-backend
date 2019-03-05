from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import (Profile, FriendRequest,
                     FriendList, BlackList,
                     UserLock, Car)

common_fields = ('id', 'user', 'created', 'modified')


class CarModelAdmin(admin.ModelAdmin):
    """Custom admin page for Car"""
    list_display = ('id', 'user', 'mark', 'model', 'created', 'modified')


class ProfileModelAdmin(admin.ModelAdmin):
    """Custom admin page for Profile"""
    readonly_fields = ('id', 'user', 'created', 'modified')
    list_display = readonly_fields
    fieldsets = (
        (_('User\'s data'), {'fields': ('user', 'first_name',
                                        'last_name', 'middle_name',
                                        'avatar', 'friends', 'blacklist')}),
        (_('Location'), {'fields': ('city', 'location')}),
        (_('Info'), {'fields': ('created', 'modified')}),
    )


class FriendRequestModelAdmin(admin.ModelAdmin):
    """Custom admin page for FriendRequest"""
    list_display = ('id', 'user', 'invited') + common_fields[-2:]


class FriendListModelAdmin(admin.ModelAdmin):
    """Custom admin page for FriendList"""
    list_display = ('id', 'owner', 'friend', 'created', 'modified')


class BlackListModelAdmin(admin.ModelAdmin):
    """Custom admin page for BlackList"""
    list_display = ('id', 'owner', 'foe', 'created', 'modified')


class UserLockModelAdmin(admin.ModelAdmin):
    """Custom admin page for UserLock"""
    list_display = common_fields


# Register your models here.
admin.site.register(Profile, ProfileModelAdmin)
admin.site.register(Car, CarModelAdmin)
admin.site.register(FriendRequest, FriendRequestModelAdmin)
admin.site.register(FriendList, FriendListModelAdmin)
admin.site.register(BlackList, BlackListModelAdmin)
admin.site.register(UserLock, UserLockModelAdmin)
