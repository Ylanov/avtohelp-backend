from django.urls import path

from base.views import current as views
from rest_framework import routers


app_name = 'base'

router = routers.SimpleRouter()
router.register(r'news', views.NewsViewSet)
router.register(r'notifications', views.NotificationViewSet)

urlpatterns = [
    path('notifications/schedule', views.PushNotificationConfigurationView.as_view(),
         name='notification-schedule'),
    path('recommendations', views.RecommendationsListView.as_view(),
         name='recommendations-list'),
    path('recommendation', views.RecommendationCreateView.as_view(),
         name='recommendation-create'),
    path('news/<int:pk>/toggle-like', views.NewsToggleLikeView.as_view(),
         name='news-like-toggle'),
    path('news/<int:pk>/comments', views.NewsCommentCreateView.as_view(),
         name='news-comment-create'),
    # path('news', views.NewsListView.as_view(), name='news-list'),
    # path('news/<int:pk>', views.NewsDetailView, name='news-detail'),
    # path('notifications', views.NotificationListView.as_view(), name='notifications-list'),
    # path('notifications/<int:pk>', views.NotificationDetailView.as_view(), name='notifications-detail'),
]

urlpatterns = router.urls + urlpatterns
