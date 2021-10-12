from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny

from catalog import models
from catalog.serializers import current as serializers

"""
VIEWSET
"""


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for City model"""

    permission_classes = (AllowAny,)
    serializer_class = serializers.CityDetailSerializer
    queryset = models.City.objects.order_by("name")
    pagination_class = None


"""
VIEWS
"""


class CityListView(generics.ListAPIView):
    """City list view"""

    permission_classes = (AllowAny,)
    serializer_class = serializers.CityListSerializer
    queryset = models.City.objects.all()
    pagination_class = None


class CityDetailView(generics.RetrieveAPIView):
    """City detail view"""

    permission_classes = (AllowAny,)
    serializer_class = serializers.CityDetailSerializer
    queryset = models.City.objects.all()
