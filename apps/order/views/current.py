from rest_framework import generics
from rest_framework.pagination import CursorPagination

from order import models
from order.serializers import current as serializers


class AssistanceRequestMixin(object):
    """AssistanceRequestMixin"""
    model = models.AssistanceRequest
    queryset = models.AssistanceRequest.objects.all()


class AssistanceRequestListView(AssistanceRequestMixin, generics.ListAPIView):
    """
    Get user assistance request list
    """
    serializer_class = serializers.AssistanceRequestListSerializer
    pagination_class = CursorPagination

    def get_queryset(self):
        """Override get_queryset method"""
        user = self.request.user
        return self.queryset.ordinary(user)


class AssistanceRequestCreateView(AssistanceRequestMixin, generics.CreateAPIView):
    """
    Create user assistance request
    REQUEST:
    {
        "issue": CharField
        "description": TextField
        "phone": PhoneNumberField
    }
    RESPONSE:
    {
      "id": 37,
      "profile": {
        "id": 1,
        "first_name": null,
        "last_name": null,
        "middle_name": null,
        "phone": "+79095499896",
        "car": {
          "id": 1,
          "mark": 1,
          "model": 1,
          "color": 1,
          "license_plate": "aa000aa 123"
        }
      },
      "issue": "Engine",
      "description": "text",
      "geo_lat": 123.124,
      "geo_lon": 123.124
    }
    """
    serializer_class = serializers.AssistanceRequestCreateSerializer


class AssistanceRequestDetailView(AssistanceRequestMixin, generics.RetrieveAPIView):
    """
    Get detail information of assistance request
    """
    serializer_class = serializers.AssistanceRequestCreateSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.by_user(user=self.request.user)


class AssistanceRequestUpdateView(AssistanceRequestMixin, generics.RetrieveUpdateAPIView):
    """
    Get detail information of assistance request
    """
    serializer_class = serializers.AssistanceRequestUpdateSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.by_user(user=self.request.user).available()


class AssistanceRequestDestroyView(generics.DestroyAPIView):
    """
   Delete assistance request
    """

    def get_queryset(self):
        """Override get_queryset method"""
        return models.AssistanceRequest.objects.by_user(user=self.request.user)
