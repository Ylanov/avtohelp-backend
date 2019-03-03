from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from account.models import User
from catalog.models import CarModel, CarMark, CarColor, City


class TestCatalog(APITestCase):
    VERSION = settings.AVAILABLE_VERSIONS.get('current')

    @classmethod
    def setUpClass(cls):
        """Set up for class"""
        print(f"\nStart test catalog app v{cls.VERSION}")
        print("==========")

    @classmethod
    def tearDownClass(cls):
        """Tear down for class"""
        print("==========")
        print(f"End test catalog app v{cls.VERSION}\n")

    def setUp(self):
        # Create users
        self.user_1 = User.objects.make(phone='+79000000001')
        self.user_2 = User.objects.make(phone='+79000000002')
        self.user_3 = User.objects.make(phone='+79000000003')
        self.users_count = User.objects.count()

        # Create car brands
        self.toyota = CarMark.objects.create(name='Toyota')
        self.nissan = CarMark.objects.create(name='Nissan')
        self.vaz = CarMark.objects.create(name='ВАЗ')
        self.car_brands = CarMark.objects.count()

        # Create car models
        self.toyota_model = CarModel.objects.create(name='Supra', mark=self.toyota)
        self.nissan_model = CarModel.objects.create(name='350Z', mark=self.nissan)
        self.vaz_model = CarModel.objects.create(name='2101', mark=self.vaz)
        self.car_models = CarModel.objects.count()

        # Create car colors
        self.color_1 = CarColor.objects.create(name='White')
        self.color_2 = CarColor.objects.create(name='Black')
        self.color_3 = CarColor.objects.create(name='Green')
        self.cars_colors = CarColor.objects.count()

        # Create cities
        self.city_1 = City.objects.create(name='Krasnodar')
        self.city_2 = City.objects.create(name='Kaliningrad')
        self.city_3 = City.objects.create(name='Novosibirsk')
        self.cities_count = City.objects.count()

    def test_list_car_colors(self):
        """Test view for getting list of users cars colors"""
        api_path = '%s:catalog:car_color_list' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.cars_colors)

    def test_car_color_detail(self):
        """Test view for getting detail of car color"""
        api_path = '%s:catalog:car_color_detail' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path, kwargs={'pk': self.color_1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cars_marks(self):
        """Test view for getting list of users cars marks"""
        api_path = '%s:catalog:car_mark_list' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.car_brands)

    def test_car_mark_detail(self):
        """Test view for getting detail of car mark"""
        api_path = '%s:catalog:car_mark_detail' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path, kwargs={'pk': self.toyota.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cars_model(self):
        """Test view for getting list of users cars model"""
        api_path = '%s:catalog:car_model_list' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.car_brands)

    def test_car_model_detail(self):
        """Test view for getting detail of car model"""
        api_path = '%s:catalog:car_model_detail' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path, kwargs={'pk': self.toyota_model.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cities(self):
        """Test view for getting list of cities"""
        api_path = '%s:catalog:city_list' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.cities_count)

    def test_city_detail(self):
        """Test view for getting detail of city"""
        api_path = '%s:catalog:city_detail' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path, kwargs={'pk': self.city_1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
