"""Version 1.0.0 url conf."""
from django.urls import path
from rest_framework import routers

from car.views import current as views

app_name = "car"

router = routers.SimpleRouter()
router.register(r"cars", views.CarViewSet)
router.register(r"colors", views.ColorsViewSet)
router.register(r"marks", views.CarMarksViewSet)
router.register(r"models", views.CarModelsViewSet)
router.register(r"service-stations", views.ServiceStationsViewSet)
router.register(
    r"service-stations-categories",
    views.ServiceStationsCategoriesViewSet,
)

urlpatterns = router.urls
