from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from account.models import User
from car.models import (CarModel, CarMark, CarColor, Car,
                        CarServiceCategory, CarService)
from userprofile.models import ProfileCar
from catalog.models import City
from django.contrib.gis.geos import Point
from rest_framework.authtoken.models import Token


class TestCatalog(APITestCase):
    VERSION = settings.AVAILABLE_VERSIONS.get('current')

    @classmethod
    def setUpClass(cls):
        """Set up for class"""
        print(f"\nStart test car app v{cls.VERSION}")
        print("==========")

    @classmethod
    def tearDownClass(cls):
        """Tear down for class"""
        print("==========")
        print(f"End test car app v{cls.VERSION}\n")

    def setUp(self):
        # Create Service Category
        self.service_cat_1 = CarServiceCategory.objects.create(name='Category 1')
        self.service_cat_2 = CarServiceCategory.objects.create(name='Category 2')

        # Create service
        self.service_1 = CarService.objects.create(category=self.service_cat_1,
                                                   description='Description',
                                                   phone='+79112223344',
                                                   location=Point(1.00000, 2.0000))
        self.service_2 = CarService.objects.create(category=self.service_cat_2,
                                                   description='Description',
                                                   phone='+79998887766',
                                                   location=Point(1.00000, 3.0000))

        # Create cities
        self.city_1 = City.objects.create(name='Krasnodar')
        self.city_2 = City.objects.create(name='Kaliningrad')
        self.city_3 = City.objects.create(name='Novosibirsk')
        self.cities_count = City.objects.count()

        # Create users
        self.user_1 = User.objects.make(phone='+79000000001', city=self.city_1)
        self.user_2 = User.objects.make(phone='+79000000002', city=self.city_2)
        self.user_3 = User.objects.make(phone='+79000000003', city=self.city_3)
        self.users_count = User.objects.count()

        # Create car brands
        self.toyota = CarMark.objects.create(name='Toyota')
        self.nissan = CarMark.objects.create(name='Nissan')
        self.vaz = CarMark.objects.create(name='ВАЗ')
        self.car_brands = CarMark.objects.count()

        # Create car models
        self.toyota_model = CarModel.objects.create(name='Supra', mark=self.toyota)
        self.toyota_model_2 = CarModel.objects.create(name='Carina', mark=self.toyota)
        self.nissan_model = CarModel.objects.create(name='350Z', mark=self.nissan)
        self.vaz_model = CarModel.objects.create(name='2101', mark=self.vaz)
        self.car_models = CarModel.objects.count()

        # Create car colors
        self.color_1 = CarColor.objects.create(name='White')
        self.color_2 = CarColor.objects.create(name='Black')
        self.color_3 = CarColor.objects.create(name='Green')
        self.cars_colors = CarColor.objects.count()

        # Create user cars
        self.car_1 = Car.objects.create(mark=self.toyota,
                                        car_model=self.toyota_model)
        self.car_2 = Car.objects.create(mark=self.toyota,
                                        car_model=self.toyota_model)
        self.car_3 = Car.objects.create(mark=self.nissan,
                                        car_model=self.nissan_model)
        self.car_4 = Car.objects.create(mark=self.vaz,
                                        car_model=self.vaz_model)
        self.car_user_1 = ProfileCar.objects.create(owner=self.user_1,
                                                    car=self.car_1,
                                                    color=self.color_1,
                                                    license_plate='aaa123aa 70')
        self.cars_count = Car.objects.count()

    def test_list_car_colors(self):
        """Test view for getting list of users cars colors"""
        api_path = '%s:car:car_color-list' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.cars_colors)

    def test_car_color_detail(self):
        """Test view for getting detail of car color"""
        api_path = '%s:car:car_color-detail' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path, kwargs={'pk': self.color_1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cars_marks_w_filters(self):
        """Test view for getting list of users cars marks with filter by model name"""
        api_path = '%s:car:car_mark-list' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path), data={'model_name': self.toyota_model.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), CarMark.objects.filter(carmodel__name=self.toyota_model.name).count())

        response = self.client.get(reverse(api_path), data={'model_id': self.toyota_model.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), CarMark.objects.filter(carmodel__id=self.toyota_model.id).count())

    def test_car_mark_detail(self):
        """Test view for getting detail of car mark"""
        api_path = '%s:car:car_mark-detail' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path, kwargs={'pk': self.toyota.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cars_model(self):
        """Test view for getting list of users cars model"""
        api_path = '%s:car:car_model-list' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.car_models)

    def test_list_cars_model_w_filters(self):
        """Test view for getting list of users cars model with filters"""
        api_path = '%s:car:car_model-list' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path), data={'mark_name': self.toyota.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), CarModel.objects.filter(mark__name=self.toyota.name).count())

        response = self.client.get(reverse(api_path), data={'mark_id': self.toyota.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), CarModel.objects.filter(mark__id=self.toyota.id).count())

    def test_car_model_detail(self):
        """Test view for getting detail of car model"""
        api_path = '%s:car:car_model-detail' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path, kwargs={'pk': self.toyota_model.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cars(self):
        """Test view for getting list of users cars"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:car:car-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.cars_count)

    def test_list_cars_w_filters(self):
        """Test view for getting list of users cars with filters"""
        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        api_path = '%s:car:car-list' % self.VERSION
        response = self.client.get(reverse(api_path), data={'mark_name': self.toyota.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Car.objects.filter(mark__name=self.toyota.name).count())

        response = self.client.get(reverse(api_path), data={'model_name': self.toyota_model.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Car.objects.filter(car_model__name=self.toyota_model.name).count())

    def test_car_detail(self):
        """Test view for getting detail of user car"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:car:car-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': self.car_1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_services_list(self):
        """Test services list view"""

        api_path = '%s:car:service-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), CarService.objects.count())

    def test_services_detail(self):
        """Test services detail view"""

        api_path = '%s:car:service-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': self.service_2.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
