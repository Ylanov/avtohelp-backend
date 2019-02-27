from rest_framework import generics

from catalog import models
from catalog.serializers import current as serializers


# Create your views here.
class CarListView(generics.ListAPIView):
    """User car list view"""

    serializer_class = serializers.CarListSerializer
    queryset = models.Car.objects.all()
    pagination_class = None


class CarDetailView(generics.RetrieveAPIView):
    """User car detail view"""

    serializer_class = serializers.CarDetailSerializer
    queryset = models.Car.objects.all()


class CarMarkListView(generics.ListAPIView):
    """Car brands list view"""

    serializer_class = serializers.CarMarkListSerializer
    queryset = models.CarMark.objects.all()
    pagination_class = None


class CarMarkDetailView(generics.RetrieveAPIView):
    """Car brands detail view"""

    serializer_class = serializers.CarMarkDetailSerializer
    queryset = models.CarMark.objects.all()


class CarColorListView(generics.ListAPIView):
    """Car brands list view"""

    serializer_class = serializers.CarColorListSerializer
    queryset = models.CarColor.objects.all()
    pagination_class = None


class CarColorDetailView(generics.RetrieveAPIView):
    """Car color detail view"""

    serializer_class = serializers.CarColorDetailSerializer
    queryset = models.CarColor.objects.all()


class CarModelListView(generics.ListAPIView):
    """Car brands list view"""

    serializer_class = serializers.CarModelListSerializer
    queryset = models.CarModel.objects.all()
    pagination_class = None


class CarModelDetailView(generics.RetrieveAPIView):
    """Car brands detail view"""

    serializer_class = serializers.CarModelDetailSerializer
    queryset = models.CarModel.objects.all()


class CityListView(generics.ListAPIView):
    """City list view"""

    serializer_class = serializers.CityListSerializer
    queryset = models.City.objects.all()
    pagination_class = None


class CityDetailView(generics.RetrieveAPIView):
    """City detail view"""

    serializer_class = serializers.CityDetailSerializer
    queryset = models.City.objects.all()
