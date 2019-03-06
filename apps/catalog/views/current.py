from rest_framework import generics
from rest_framework.permissions import AllowAny

from catalog import models
from catalog.serializers import current as serializers


# Create your views here.
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
