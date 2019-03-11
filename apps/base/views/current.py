from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from base import models
from base.serializers import current as serializers


# Create your views here.
class NewsListView(generics.ListAPIView):
    """
    News list view
    """

    permission_classes = (AllowAny,)
    model = models.Newsletter
    queryset = models.Newsletter.objects.all()
    serializer_class = serializers.NewsListSerializer


class NewsDetailView(generics.RetrieveAPIView):
    """
    News detail view
    """

    permission_classes = (AllowAny,)
    model = models.Newsletter
    queryset = models.Newsletter.objects.all()
    serializer_class = serializers.NewsDetailSerializer


class NotificationListView(generics.ListAPIView):
    """
    Push-notification list view
    """

    permission_classes = (AllowAny,)  # NOTE: rly?
    serializer_class = serializers.NotificationListSerializer
    queryset = models.PushNotification.objects.all()
    # NOTE: PushNotification.user is Foreign key
    # TODO: change get_queryset method to filter it by request.user 


class NotificationDetailView(generics.RetrieveAPIView):
    """
    Push-notification detail view
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.NotificationListSerializer
    queryset = models.PushNotification.objects.all()
