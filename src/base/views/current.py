from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from base import models
from base.serializers import current as serializers
from utils import views as view_mixins
from utils.paginations import NewsCursorPagination, ProjectCursorPagination

"""
VIEWSETS
"""


class NewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for model News
    """

    permission_classes = (AllowAny,)
    model = models.Newsletter
    queryset = models.Newsletter.objects.filter(publish=True)
    serializer_class = serializers.NewsDetailSerializer
    pagination_class = NewsCursorPagination


class NotificationViewSet(view_mixins.NotificationViewMixin, viewsets.ModelViewSet):
    """
    ViewSet for model Notification
    """

    serializer_class = serializers.NotificationDetailSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.filter(user=self.request.user)


"""
VIEWS
"""


class PushNotificationConfigurationView(generics.GenericAPIView):
    """
    Generics for singleton model PushNotificationConfiguration
    """

    serializer_class = serializers.PushNotificationScheduleSerializer

    def get(self, request, *args, **kwargs):
        """Override get method"""
        obj = models.PushNotificationConfiguration.get_solo()
        return Response(
            data=self.get_serializer(obj.notification_schedule, many=True).data
        )


class RecommendationsListView(generics.ListAPIView):
    """
    Recommendations list view
    """

    # permission_classes = (AllowAny,)
    serializer_class = serializers.RecommendationsListSerializer
    queryset = models.Newsletter.objects.all()
    pagination_class = ProjectCursorPagination

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.filter(author_id=self.request.user.id)


class RecommendationCreateView(generics.CreateAPIView):
    """
    Recommendation create view
    """

    serializer_class = serializers.RecommendationCreateSerializer


class NewsToggleLikeView(generics.UpdateAPIView):
    """
    News toggle like view
    """

    queryset = models.Newsletter.objects.all()
    serializer_class = serializers.NewsToggleLikeSerializer


class NewsCommentCreateView(generics.CreateAPIView):
    """
    News comment create view
    """

    queryset = models.NewsletterComment.objects.all()
    serializer_class = serializers.NewsletterCommentCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # add things in context.
        context["newsletter_id"] = self.kwargs["newsletter_id"]
        return context


class NewsCommentUpdateView(generics.UpdateAPIView):
    queryset = models.NewsletterComment.objects.all()
    serializer_class = serializers.NewsletterCommentUpdateSerializer


class NewsCommentDeleteView(generics.DestroyAPIView):
    queryset = models.NewsletterComment.objects.all()
    serializer_class = serializers.NewsletterCommentDeleteSerializer


# class NewsListView(generics.ListAPIView):
#     """
#     News list view
#     """
#
#     permission_classes = (AllowAny,)
#     model = models.Newsletter
#     queryset = models.Newsletter.objects.all()
#     serializer_class = serializers.NewsListSerializer
#
#
# class NewsDetailView(generics.RetrieveAPIView):
#     """
#     News detail view
#     """
#
#     permission_classes = (AllowAny,)
#     model = models.Newsletter
#     queryset = models.Newsletter.objects.all()
#     serializer_class = serializers.NewsDetailSerializer
#
#
# class NotificationListView(view_mixins.NotificationViewMixin, generics.ListAPIView):
#     """
#     Push-notification list view
#     """
#
#     serializer_class = serializers.NotificationListSerializer
#
#     def get_queryset(self):
#         """Override get_queryset method"""
#         return self.queryset.filter(user=self.request.user)
#
#
# class NotificationDetailView(view_mixins.NotificationViewMixin, generics.RetrieveAPIView):
#     """
#     Push-notification detail view
#     """
#
#     serializer_class = serializers.NotificationDetailSerializer
