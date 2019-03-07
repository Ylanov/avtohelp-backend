"""Version 1.0.0 url conf."""
from django.urls import path
from authorization.views import current as views


app_name = 'authorization'

urlpatterns = [
    path('verify', views.PhoneVerificationView.as_view(), name='verify'),
    path('auth', views.AuthorizationView.as_view(), name='auth'),
    path('logout', views.LogoutView.as_view(), name='logout'),
]
