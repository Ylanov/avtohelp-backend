from rest_framework import generics
from rest_framework.permissions import AllowAny

from car import models
from car.serializers import current as serializers


# Create your views here.
class CarListView(generics.ListAPIView):
    """Car list view"""

    serializer_class = serializers.CarListSerializer
    queryset = models.Car.objects.all()
    pagination_class = None


class CarDetailView(generics.RetrieveUpdateAPIView):
    """User car detail view"""

    serializer_class = serializers.CarDetailSerializer
    queryset = models.Car.objects.all()


class CarMarkListView(generics.ListAPIView):
    """Car brands list view"""

    permission_classes = (AllowAny,)
    serializer_class = serializers.CarMarkListSerializer
    queryset = models.CarMark.objects.all()
    pagination_class = None


class CarMarkDetailView(generics.RetrieveAPIView):
    """Car brands detail view"""

    permission_classes = (AllowAny,)
    serializer_class = serializers.CarMarkDetailSerializer
    queryset = models.CarMark.objects.all()


class CarColorListView(generics.ListAPIView):
    """Car brands list view"""

    permission_classes = (AllowAny,)
    serializer_class = serializers.CarColorListSerializer
    queryset = models.CarColor.objects.all()
    pagination_class = None


class CarColorDetailView(generics.RetrieveAPIView):
    """Car color detail view"""

    permission_classes = (AllowAny,)
    serializer_class = serializers.CarColorDetailSerializer
    queryset = models.CarColor.objects.all()


class CarModelListView(generics.ListAPIView):
    """Car brands list view"""

    permission_classes = (AllowAny,)
    serializer_class = serializers.CarModelListSerializer
    queryset = models.CarModel.objects.all()
    pagination_class = None


class CarModelDetailView(generics.RetrieveAPIView):
    """Car brands detail view"""

    permission_classes = (AllowAny,)
    serializer_class = serializers.CarModelDetailSerializer
    queryset = models.CarModel.objects.all()


class CarServiceStationListView(generics.ListAPIView):
    """
    ServiceStations list view
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.ServiceListSerializer
    queryset = models.CarService.objects.all()


class CarServiceStationDetailView(generics.RetrieveAPIView):
    """
    ServiceStations detail view
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.ServiceDetailSerializer
    queryset = models.CarService.objects.all()
