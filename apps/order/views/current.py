from rest_framework import generics, views, status
from rest_framework.response import Response

from base.models import PushNotificationConfiguration
from order import models, filters
from order.serializers import current as serializers


class AssistanceRequestBaseMixin:
    """AssistanceRequest mixin"""

    queryset = models.AssistanceRequest.objects.select_related('user__profile')


class AssistanceRequestMixin(AssistanceRequestBaseMixin):
    """AssistanceRequestMixin"""

    model = models.AssistanceRequest

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.available(self.request.user)\
                            .annotate_distance(raw_coordinates=self.request.query_params.get('coordinates'))


class AssistanceRequestListView(AssistanceRequestMixin, generics.ListAPIView):
    """
    Get user assistance request list w/ filters by fields:
    - profile_id
    - coordinates
    ordering by:
    - distance
    """
    serializer_class = serializers.AssistanceRequestListSerializer
    pagination_class = None
    filter_class = filters.AssistanceRequestFitlerSet

    def get_queryset(self):
        return super().get_queryset().annotate_owner_status(user=self.request.user)


class AssistanceRequestCountView(views.APIView):
    """
    Return count of available assistance request
    """
    def get(self, request, *args, **kwargs):
        """Get count of assistance requests"""
        user = request.user
        push_config = PushNotificationConfiguration.get_solo()
        if user.location_is_valid:
            return Response({
                'count': models.AssistanceRequest.objects.available(user)\
                                                         .annotate_distance(point=user.profilelocation.location)\
                                                         .filter(distance__lte=push_config.radius)\
                                                         .count()
            })
        else:
            return Response({
                'count': 0
            })


class AssistanceRequestCreateView(AssistanceRequestBaseMixin, generics.CreateAPIView):
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
        return super().get_queryset()


class AssistanceRequestDetailView(AssistanceRequestBaseMixin, generics.RetrieveAPIView):
    """
    Get detail information of assistance request
    """
    serializer_class = serializers.AssistanceRequestCreateSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return super().get_queryset().annotate_distance(raw_coordinates=self.request.query_params.get('coordinates'))\
                                     .annotate_owner_status(user=self.request.user)


class AssistanceRequestUpdateView(AssistanceRequestBaseMixin, generics.UpdateAPIView):
    """
    Get detail information of assistance request
    """
    serializer_class = serializers.AssistanceRequestUpdateSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return super().get_queryset().by_user(user=self.request.user)\
                                     .available(user=self.request.user)


class AssistanceRequestView(AssistanceRequestBaseMixin, generics.RetrieveDestroyAPIView):
    """
    Get detail information of assistance request
    """
    serializer_class = serializers.AssistanceRequestCreateSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return super().get_queryset().annotate_distance(raw_coordinates=self.request.query_params.get('coordinates'))


class AssistanceRequestDestroyView(generics.DestroyAPIView):
    """
   Delete assistance request
    """

    def get_queryset(self):
        """Override get_queryset method"""
        return models.AssistanceRequest.objects.by_user(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = models.AssistanceRequest.CANCELED
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
