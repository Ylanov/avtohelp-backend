from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import (Profile, FriendRequest,
                     FriendList, BlackList,
                     ProfileLocation, ProfileCar,
                     ProfileGallery)

common_fields = ('id', 'user', 'created', 'modified')


class ProfileGalleryInline(admin.TabularInline):
    """Inline for model Profile"""
    model = ProfileGallery
    classes = ['collapse']
    extra = 1


class ProfileModelAdmin(admin.ModelAdmin):
    """Custom admin page for Profile"""
    readonly_fields = ('id', 'created', 'modified')
    inlines = (ProfileGalleryInline, )
    list_display = readonly_fields + ('user',)
    fieldsets = (
        (_('User\'s data'), {'fields': ('user', 'first_name',
                                        'last_name', 'middle_name')}),
        (_('Location'), {'fields': ('city',)}),
        (_('Info'), {'fields': ('created', 'modified')}),
    )


class FriendRequestModelAdmin(admin.ModelAdmin):
    """Custom admin page for FriendRequest"""
    list_display = ('id', 'owner', 'invited') + common_fields[-2:]


class ProfileLocationModelAdmin(admin.ModelAdmin):
    """Custom admin page for FriendRequest"""
    list_display = ('id', 'user', 'location') + common_fields[-2:]


class FriendListModelAdmin(admin.ModelAdmin):
    """Custom admin page for FriendList"""
    list_display = ('id', 'owner', 'friend', 'created', 'modified')


class BlackListModelAdmin(admin.ModelAdmin):
    """Custom admin page for BlackList"""
    list_display = ('id', 'owner', 'foe', 'created', 'modified')


class ProfileCarModelAdmin(admin.ModelAdmin):
    """Custom admin page for ProfileCar"""
    list_display = ('id', 'owner', 'car', 'license_plate')


class ProfileGalleryModelAdmin(admin.ModelAdmin):
    """Custom admin page for ProfileGallery"""
    list_display = ('id', 'profile', 'image')


# Register your models here.
admin.site.register(Profile, ProfileModelAdmin)
admin.site.register(ProfileLocation, ProfileLocationModelAdmin)
admin.site.register(ProfileGallery, ProfileGalleryModelAdmin)
admin.site.register(FriendRequest, FriendRequestModelAdmin)
admin.site.register(FriendList, FriendListModelAdmin)
admin.site.register(BlackList, BlackListModelAdmin)
admin.site.register(ProfileCar, ProfileCarModelAdmin)