from django.contrib import admin
from .models import Newsletter, PushNotification


# Register your models here.
admin.site.register(Newsletter)
admin.site.register(PushNotification)
