"""Project URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view

from base.views import common as base_views
from project.urls import current, future
from userprofile.views import current as views

api_schema_view = get_swagger_view(title='Road Helper API')
current_version = settings.AVAILABLE_VERSIONS.get('current')
future_version = settings.AVAILABLE_VERSIONS.get('future')
urlpatterns = [
    path('app', base_views.IndexView.as_view()),

    path('admin/', admin.site.urls),
    path(f'api/v{current_version}/', include(current, namespace=f'{current_version}')),
    path(f'api/v{future_version}/', include(future, namespace=f'{future_version}')),
    path('version/', include('versioning.urls')),
    path('device', views.FCMDeviceViewSet.as_view(), name='fcm_device_create'),
    path('swagger/', api_schema_view),

    path('documentation/', include('documentation.urls', namespace='documentation'))

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
