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


class ServiceStationListView(generics.ListAPIView):
    """
    ServiceStations list view
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.ServiceListSerializer
    queryset = models.Service.objects.all()


class ServiceStationDetailView(generics.RetrieveAPIView):
    """
    ServiceStations detail view
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.ServiceDetailSerializer
    queryset = models.Service.objects.all()


class NotificationListView(generics.ListAPIView):
    """
    Push-notification list view
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.NotificationListSerializer
    queryset = models.PushNotification.objects.all()


class NotificationDetailView(generics.RetrieveAPIView):
    """
    Push-notification detail view
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.NotificationListSerializer
    queryset = models.PushNotification.objects.all()
