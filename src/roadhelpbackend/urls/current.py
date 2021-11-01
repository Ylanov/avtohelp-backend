"""Version 1.0.0 url conf."""
from django.urls import include, path

app_name = "current"

urlpatterns = [
    path("authorization/", include("authorization.urls.current")),
    path("base/", include("base.urls.current")),
    path("car/", include("car.urls.current")),
    path("catalog/", include("catalog.urls.current")),
    path("userprofile/", include("userprofile.urls")),
    path("order/", include("order.urls.current")),
    path("chat/", include("chat.urls")),
]
