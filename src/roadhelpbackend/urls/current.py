"""Version 1.0.0 url conf."""
from django.urls import include, path

from base.views.common import GeneralInfoView

app_name = "current"

urlpatterns = [
    path("authorization/", include("authorization.urls.current")),
    path("base/", include("base.urls.current")),
    path("car/", include("car.urls.current")),
    path("catalog/", include("catalog.urls.current")),
    path("userprofile/", include("userprofile.urls")),
    path("order/", include("order.urls.current")),
    path("chat/", include("chat.urls")),
    # Bootstrap endpoint consumed by the Android app; kept verbatim from the
    # API contract (client calls "api/general_info" relative to baseURL).
    path("api/general_info", GeneralInfoView.as_view(), name="general-info"),
]
