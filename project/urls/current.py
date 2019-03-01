"""Version 1.0.0 url conf."""
from django.urls import path, include


app_name = 'current'

urlpatterns = [
    path('authorization/', include('authorization.urls.current')),
    path('catalog/', include('catalog.urls.current')),
    path('userprofile/', include('userprofile.urls.current')),
    path('order/', include('order.urls.current')),
]
