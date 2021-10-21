from django.contrib.gis.geos import Point
from rest_framework import viewsets
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly,
)

from car import (
    filters,
    models,
)
from car.serializers import current as serializers

"""
VIEWSETS
"""


class CarViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for model CarViewSet
    """

    serializer_class = serializers.CarDetailSerializer
    filter_class = filters.CarListFilterSet
    queryset = models.Car.objects.select_related(
        "mark", "car_model__mark"
    ).all()
    pagination_class = None
    permission_classes = (AllowAny,)


class ColorsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for model ColorsViewSet
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = serializers.CarColorDetailSerializer
    queryset = models.CarColor.objects.exclude(hex_color__isnull=True)
    filter_class = filters.CarColorFilterSet
    pagination_class = None


class CarMarksViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for model MarksViewSet
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.CarMarkDetailSerializer
    queryset = models.CarMark.objects.all()
    filter_class = filters.CarMarkListFilterSet
    pagination_class = None


class CarModelsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for model ModelsViewSet
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.CarModelDetailSerializer
    queryset = models.CarModel.objects.all()
    filter_class = filters.CarModelListFilterSet


class ServiceStationsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for model ServiceStationsViewSet
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.ServiceListSerializer
    filter_class = filters.ServiceStationsFilterSet
    queryset = models.CarService.objects.annotate_icon_exists()
    pagination_class = None

    def get_queryset(self):
        """Override get_queryset method"""
        query = self.request.query_params.get("position")
        if query:
            position_x = float(query.split(",")[0])
            position_y = float(query.split(",")[1])
            # Point(longitude, latitude)
            position = Point(position_x, position_y, srid=4326)
            return self.queryset.annotate_distance(position)
        return self.queryset


class ServiceStationsCategoriesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for model ServiceStationsViewSet
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.ServiceStationsCategoriesSerializer
    queryset = models.CarServiceCategory.objects.all()
    pagination_class = None
