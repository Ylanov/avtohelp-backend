from django.contrib import admin
from .models import (Profile, FriendRequest,
                     FriendList, BlackList,
                     UserLock)


# Register your models here.
admin.site.register(Profile)
admin.site.register(FriendRequest)
admin.site.register(FriendList)
admin.site.register(BlackList)
admin.site.register(UserLock)
