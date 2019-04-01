from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny

from base import models
from base.serializers import current as serializers
from utils import views as view_mixins


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

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.order_by('-publish', '-publish_date')


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
