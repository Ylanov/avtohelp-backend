from rest_framework import generics, views
from rest_framework.response import Response

from order import models, filters
from order.serializers import current as serializers


class AssistanceRequestMixin(object):
    """AssistanceRequestMixin"""
    model = models.AssistanceRequest
    queryset = models.AssistanceRequest.objects.all()

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.available(self.request.user).annotate_distance(
            raw_coordinates=self.request.query_params.get('coordinates'))


class AssistanceRequestListView(AssistanceRequestMixin, generics.ListAPIView):
    """
    Get user assistance request list w/ filters by fields
    profile_id
    distance
    """
    serializer_class = serializers.AssistanceRequestListSerializer
    pagination_class = None
    filter_class = filters.AssistanceRequestFitlerSet


class AssistanceRequestCountView(views.APIView):
    """
    Return count of available assistance request
    """
    def get(self, request, *args, **kwargs):
        """Get count of assistance requests"""
        return Response({'count': models.AssistanceRequest.objects.available(user=request.user).count()})


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

    def get_queryset(self):
        return self.queryset.available(self.request.user).annotate_distance(
            raw_coordinates=self.request.query_params.get('coordinates'))


class AssistanceRequestDetailView(generics.RetrieveAPIView):
    """
    Get detail information of assistance request
    """
    serializer_class = serializers.AssistanceRequestCreateSerializer
    queryset = models.AssistanceRequest.objects.all()

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.all().annotate_distance(
            raw_coordinates=self.request.query_params.get('coordinates'))


class AssistanceRequestUpdateView(AssistanceRequestMixin, generics.UpdateAPIView):
    """
    Get detail information of assistance request
    """
    serializer_class = serializers.AssistanceRequestUpdateSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.by_user(user=self.request.user).available(user=self.request.user)


class AssistanceRequestDestroyView(generics.DestroyAPIView):
    """
   Delete assistance request
    """

    def get_queryset(self):
        """Override get_queryset method"""
        return models.AssistanceRequest.objects.by_user(user=self.request.user)
