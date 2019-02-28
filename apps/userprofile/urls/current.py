"""Version 1.0.0 url conf."""
from django.urls import path
from userprofile.views import current as views


app_name = 'userprofile'

urlpatterns = [
    path('device', views.FCMDeviceViewSet.as_view(), name='device'),
    path('profile', views.ProfileView.as_view(), name='profile'),
]
