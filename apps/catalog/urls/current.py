"""Version 1.0.0 url conf."""
from django.urls import path
from catalog.views import current as views


app_name = 'catalog'

urlpatterns = [
    path('cities', views.CityListView.as_view(),  name='city_list'),
    path('cities/<int:pk>', views.CityDetailView.as_view(),  name='city_detail'),
]
