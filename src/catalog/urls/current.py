"""Version 1.0.0 url conf."""
from django.urls import path
from rest_framework import routers

from catalog.views import current as views

app_name = "catalog"

router = routers.SimpleRouter()
router.register(r"cities", views.CityViewSet)

# urlpatterns = [
#     path('cities', views.CityListView.as_view(),  name='city-list'),
#     path('cities/<int:pk>', views.CityDetailView.as_view(),  name='city-detail'),
# ]

urlpatterns = router.urls
