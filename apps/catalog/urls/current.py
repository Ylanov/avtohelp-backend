"""Version 1.0.0 url conf."""
from django.urls import path
from catalog.views import current as views


app_name = 'catalog'

urlpatterns = [
    path('cars', views.CarListView.as_view(),  name='car_list'),
    path('cars/<int:pk>', views.CarDetailView.as_view(),  name='car_detail'),
    path('cars/colors', views.CarColorListView.as_view(),  name='car_color_list'),
    path('cars/colors/<int:pk>', views.CarColorDetailView.as_view(),  name='car_color_detail'),
    path('cars/marks', views.CarMarkListView.as_view(),  name='car_mark_list'),
    path('cars/marks/<int:pk>', views.CarMarkDetailView.as_view(),  name='car_mark_detail'),
    path('cars/models', views.CarModelListView.as_view(),  name='car_model_list'),
    path('cars/models/<int:pk>', views.CarMarkDetailView.as_view(),  name='car_model_detail'),
    path('cities', views.CityListView.as_view(),  name='city_list'),
    path('cities/<int:pk>', views.CityDetailView.as_view(),  name='city_detail'),
]
