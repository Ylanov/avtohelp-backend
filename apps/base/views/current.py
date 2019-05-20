from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from base import models
from base.serializers import current as serializers
from utils import views as view_mixins
from utils.paginations import NewsCursorPagination

"""
VIEWSETS
"""


class NewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for model News
    """
    permission_classes = (AllowAny,)
    model = models.Newsletter
    queryset = models.Newsletter.objects.all()
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
        return Response(data=self.get_serializer(obj.notification_schedule, many=True).data)


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
