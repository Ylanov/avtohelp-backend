from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from order import models
from order.serializers import current as serializers


class AssistanceRequestListView(generics.ListAPIView):
    """
    Get user assistance request list
    """

    model = models.AssistanceRequest
    queryset = models.AssistanceRequest.objects.all()
    serializer_class = serializers.AssistanceRequestListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.by_user(user=self.request.user)
