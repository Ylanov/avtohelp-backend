"""Version 1.0.0 url conf."""
from django.urls import path

from car.views import current as views

app_name = 'car'

urlpatterns = [
    path('', views.CarListView.as_view(), name='car-list'),
    path('<int:pk>', views.CarDetailView.as_view(), name='car-detail'),
    path('colors', views.CarColorListView.as_view(), name='car_color-list'),
    path('colors/<int:pk>', views.CarColorDetailView.as_view(), name='car_color-detail'),
    path('marks', views.CarMarkListView.as_view(), name='car_mark-list'),
    path('marks/<int:pk>', views.CarMarkDetailView.as_view(), name='car_mark-detail'),
    path('models', views.CarModelListView.as_view(), name='car_model-list'),
    path('models/<int:pk>', views.CarModelDetailView.as_view(), name='car_model-detail'),
    path('service-stations', views.CarServiceStationListView.as_view(), name='service-list'),
    path('service-stations/<int:pk>', views.CarServiceStationDetailView.as_view(), name='service-detail'),

]
