from rest_framework import serializers
from car import models
from utils.serializers import CoordinatesSerializer
from os.path import exists


class CarListSerializer(serializers.ModelSerializer):
    """Car list serializer"""

    mark_name = serializers.CharField(source='mark.name')
    model_name = serializers.CharField(source='car_model.name')

    class Meta:
        """Meta model"""

        model = models.Car
        fields = ('id', 'created', 'mark_name', 'model_name')


class CarMarkListSerializer(serializers.ModelSerializer):
    """Car brand list serializer"""

    class Meta:
        """Meta model"""

        model = models.CarMark
        fields = ('id', 'created', 'name')


class CarMarkDetailSerializer(serializers.ModelSerializer):
    """Car brand detail serializer"""

    class Meta:
        """Meta model"""

        model = models.CarMark
        fields = ('id', 'created', 'name')


class CarModelListSerializer(serializers.ModelSerializer):
    """Car model list serializer"""

    class Meta:
        """Meta model"""

        model = models.CarModel
        fields = ('id', 'created', 'name')


class CarModelDetailSerializer(serializers.ModelSerializer):
    """Car model detail serializer"""

    class Meta:
        """Meta model"""

        model = models.CarModel
        fields = ('id', 'created', 'name')


class CarColorListSerializer(serializers.ModelSerializer):
    """Car color list serializer"""

    class Meta:
        """Meta model"""

        model = models.CarColor
        fields = ('id', 'created', 'name')


class CarColorDetailSerializer(serializers.ModelSerializer):
    """Car color detail serializer"""

    class Meta:
        """Meta model"""

        model = models.CarColor
        fields = ('id', 'created', 'name')


class CarDetailSerializer(serializers.ModelSerializer):
    """Car detail serializer"""

    mark = CarMarkDetailSerializer()
    model = CarModelDetailSerializer(source='car_model')

    class Meta:
        """Meta model"""

        model = models.Car
        fields = ('id', 'created', 'mark', 'model')


class CarServiceCategorySerializer(serializers.ModelSerializer):
    """Serializer for model CarServiceCategory"""

    icon = serializers.SerializerMethodField()

    class Meta:
        """Meta model"""
        model = models.CarServiceCategory
        fields = ('id', 'name', 'icon')

    def get_icon(self, obj):
        """Get icon"""
        return obj.get_full_image_url(request=self.context.get('request'))


class ServiceListSerializer(serializers.ModelSerializer, CoordinatesSerializer):
    """Service list serializer"""

    distance = serializers.SerializerMethodField()
    category_detail = serializers.SerializerMethodField()

    class Meta:
        """Meta model"""

        model = models.CarService
        fields = ('id', 'created', 'name', 'geo_lat', 'geo_lon', 'category_detail', 'distance')

    def get_distance(self, obj):
        """Get distance in meters"""
        return obj.distance.m if hasattr(obj, 'distance') else None

    def get_category_detail(self, obj):
        """Method to get category"""
        return CarServiceCategorySerializer(obj.category, context={'request': self.context.get('request')}).data


class ServiceStationsCategoriesSerializer(serializers.ModelSerializer):
    """Service list serializer"""

    class Meta:
        """Meta model"""

        model = models.CarServiceCategory
        fields = ('id', 'name', 'image')


class ServiceDetailSerializer(serializers.ModelSerializer, CoordinatesSerializer):
    """Service detail serializer"""

    class Meta:
        """Meta model"""

        model = models.CarService
        fields = ('id', 'created', 'modified', 'name',
                  'category_id', 'description', 'geo_lat',
                  'geo_lon', 'phone')
