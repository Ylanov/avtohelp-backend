from rest_framework import routers

from catalog.views import current as views

app_name = "catalog"

router = routers.SimpleRouter()
router.register(r"cities", views.CityViewSet)

urlpatterns = router.urls
