from django.urls import path
from rest_framework.routers import SimpleRouter

from base.views import current as views

app_name = "base"


class BaseSimpleRouter(SimpleRouter):
    """SimpleRouter subclass that allows an optional trailing slash.

    Important: `super(SimpleRouter, self).__init__()` in the old code was
    a bug — it SKIPS SimpleRouter.__init__ and calls BaseRouter.__init__
    instead. That worked by accident on DRF 3.9, but DRF 3.15 moved
    `_use_regex` initialisation into SimpleRouter.__init__, so skipping
    it now crashes with:
        AttributeError: 'BaseSimpleRouter' object has no attribute '_use_regex'
    The fix is to call super().__init__() so SimpleRouter's setup actually runs.
    """

    def __init__(self):
        super().__init__()
        self.trailing_slash = "/?"


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
