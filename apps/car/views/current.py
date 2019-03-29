from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly

from car import models, filters
from django.db.models import ExpressionWrapper, IntegerField, F
from django.contrib.gis.geos import Point
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
    queryset = models.Car.objects.select_related('mark', 'car_model__mark').all()
    pagination_class = None


class ColorsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for model ColorsViewSet
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = serializers.CarColorDetailSerializer
    queryset = models.CarColor.objects.all()
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
    pagination_class = None


class ServiceStationsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for model ServiceStationsViewSet
    """
    permission_classes = (AllowAny,)
    serializer_class = serializers.ServiceListSerializer
    filter_class = filters.ServiceStationsFilterSet
    queryset = models.CarService.objects.all()

    def get_queryset(self):
        """Override get_queryset method"""
        query = self.request.query_params.get('position')
        if query:
            position_x = float(query.split(',')[0])
            position_y = float(query.split(',')[1])
            position = Point(position_x, position_y, srid=4326)
            return self.queryset.annotate_distance(position)


"""
VIEWS
"""


class CarListView(generics.ListAPIView):
    """
    Car list view
    With filter by fields:
    :param mark_name: Search profile by car mark name
    :param model_name: Search profile by car model name
    :param car_model: Search profile by car model ID
    :param mark: Search profile by car mark ID
    :type mark_name: CharField Toyota
    :type model_name: CharField Supra
    :type car_model: IntegerField 1
    :type mark: IntegerField 2
    """

    serializer_class = serializers.CarListSerializer
    filter_class = filters.CarListFilterSet
    queryset = models.Car.objects.select_related('mark', 'car_model__mark').all()
    pagination_class = None


class CarDetailView(generics.RetrieveUpdateAPIView):
    """User car detail view"""

    serializer_class = serializers.CarDetailSerializer
    queryset = models.Car.objects.all()


class CarMarkListView(generics.ListAPIView):
    """
    Car brands list view
    With filter by fields:
    :param model_name: Search by field car model name
    :param model_id: Search by field car model id
    :type model_name: CharField Caldina
    :type model_id: IntegerField 1
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.CarMarkListSerializer
    queryset = models.CarMark.objects.all()
    filter_class = filters.CarMarkListFilterSet
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
    """
    Car model list view
    With filter by fields:
    :param mark_name: Search by field car mark name
    :param mark_id: Search by field car mark id
    :type mark_name: CharField Toyota
    :type mark_id: IntegerField 1
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.CarModelListSerializer
    queryset = models.CarModel.objects.all()
    filter_class = filters.CarModelListFilterSet
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
