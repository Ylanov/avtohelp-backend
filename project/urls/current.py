"""Version 1.0.0 url conf."""
from django.urls import path, include


app_name = 'current'

urlpatterns = [
    path('catalog/', include('catalog.urls.current')),
]
