"""Version 1.0.0 url conf."""
from django.urls import path
from authorization.views import current as views


app_name = 'authorization'

urlpatterns = [
    path('', views.AuthorizationView.as_view(),  name='authorization'),
    path('verify', views.PhoneVerificationView.as_view(), name='verify'),
    path('authentication', views.AuthenticationView.as_view(), name='authentication'),
    path('logout', views.LogoutView.as_view(), name='logout'),
]