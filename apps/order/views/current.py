from rest_framework import generics, views
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination

from order import models, filters
from order.serializers import current as serializers
from django.contrib.gis.geos import Point


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
    filter_class = filters.AssistanceRequestFitlerSet

    def get_queryset(self):
        """Override get_queryset method"""
        qs = self.queryset.available(self.request.user)
        query = self.request.query_params.get('position')
        if query:
            position_x = float(query.split(',')[0])
            position_y = float(query.split(',')[1])
            position = Point(position_x, position_y, srid=4326)
            return qs.annotate_distance(position)
        return qs


class AssistanceRequestCountView(views.APIView):
    """
    Return count of availbale assistance request
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
