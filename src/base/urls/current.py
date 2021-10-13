from django.urls import path
from rest_framework.routers import SimpleRouter

from base.views import current as views

app_name = "base"


class BaseSimpleRouter(SimpleRouter):
    def __init__(self):
        self.trailing_slash = "/?"
        super(SimpleRouter, self).__init__()


router = BaseSimpleRouter()

router.register(r"news", views.NewsViewSet)
router.register(r"notifications", views.NotificationViewSet)

urlpatterns = [
    path(
        "notifications/schedule",
        views.PushNotificationConfigurationView.as_view(),
        name="notification-schedule",
    ),
    path(
        "recommendations",
        views.RecommendationsListView.as_view(),
        name="recommendations-list",
    ),
    path(
        "recommendation",
        views.RecommendationCreateView.as_view(),
        name="recommendation-create",
    ),
    path(
        "news/<int:pk>/toggle-like",
        views.NewsToggleLikeView.as_view(),
        name="news-like-toggle",
    ),
    path(
        "news/<int:newsletter_id>/comments",
        views.NewsCommentCreateView.as_view(),
        name="news-comment-create",
    ),
    path(
        "comments/<int:pk>",
        views.NewsCommentUpdateView.as_view(),
        name="news-comment-update",
    ),
    path(
        "comments/<int:pk>/delete",
        views.NewsCommentDeleteView.as_view(),
        name="news-comment-delete",
    ),
]

urlpatterns = router.urls + urlpatterns
