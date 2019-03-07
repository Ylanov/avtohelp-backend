from django.urls import path

from base.views import current as views

app_name = 'base'

urlpatterns = [
    path('news', views.NewsListView.as_view(), name='news-list'),
    path('news/<int:pk>', views.NewsDetailView.as_view(), name='news-detail'),
    path('notifications', views.NotificationListView.as_view(), name='notifications-list'),
    path('notifications/<int:pk>', views.NotificationDetailView.as_view(), name='notifications-detail'),
]
