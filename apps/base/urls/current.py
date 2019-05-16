from django.urls import path

from base.views import current as views
from rest_framework import routers


app_name = 'base'

router = routers.SimpleRouter()
router.register(r'news', views.NewsViewSet)
router.register(r'notifications', views.NotificationViewSet)

urlpatterns = [
    path('notifications/configuration', views.PushNotificationConfigurationView.as_view(),
         name='notification-configuration')
    # path('news', views.NewsListView.as_view(), name='news-list'),
    # path('news/<int:pk>', views.NewsDetailView, name='news-detail'),
    # path('notifications', views.NotificationListView.as_view(), name='notifications-list'),
    # path('notifications/<int:pk>', views.NotificationDetailView.as_view(), name='notifications-detail'),
]

urlpatterns = router.urls + urlpatterns
