from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from account.models import User
from catalog.models import City ,CarColor, CarMark, CarModel
from userprofile.models import Car


class TestCatalog(APITestCase):
    VERSION = settings.AVAILABLE_VERSIONS.get('current')

    @classmethod
    def setUpClass(cls):
        """Set up for class"""
        print(f"\nStart test authorization app v{cls.VERSION}")
        print("==========")

    @classmethod
    def tearDownClass(cls):
        """Tear down for class"""
        print("==========")
        print(f"End test authorization app v{cls.VERSION}\n")

    def setUp(self):
        # Create cities
        self.city_1 = City.objects.create(name='Krasnodar')
        self.city_2 = City.objects.create(name='Kaliningrad')
        self.city_3 = City.objects.create(name='Novosibirsk')

        # Create users
        self.user_1 = User.objects.make(phone='+79000000001')
        self.user_2 = User.objects.make(phone='+79000000002')
        self.user_3 = User.objects.make(phone='+79000000003')

        # Create car brands
        self.toyota = CarMark.objects.create(name='Toyota')
        self.nissan = CarMark.objects.create(name='Nissan')
        self.vaz = CarMark.objects.create(name='ВАЗ')
        self.car_brands = CarMark.objects.count()

        # Create car models
        self.toyota_model = CarModel.objects.create(name='Supra', mark=self.toyota)
        self.nissan_model = CarModel.objects.create(name='350Z', mark=self.nissan)
        self.vaz_model = CarModel.objects.create(name='2101', mark=self.vaz)

        # Create car colors
        self.color_1 = CarColor.objects.create(name='White')
        self.color_2 = CarColor.objects.create(name='Black')
        self.color_3 = CarColor.objects.create(name='Green')

        # Create user cars
        self.car_1 = Car.objects.create(user=self.user_1,
                                        mark=self.toyota,
                                        model=self.toyota_model,
                                        color=self.color_1)
        self.car_2 = Car.objects.create(user=self.user_2,
                                        mark=self.nissan,
                                        model=self.nissan_model,
                                        color=self.color_2)
        self.car_3 = Car.objects.create(user=self.user_3,
                                        mark=self.vaz,
                                        model=self.vaz_model,
                                        color=self.color_3)
        self.cars_count = Car.objects.count()

    def test_retrieving_profile(self):
        """Test view for retrieving user profile"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:profile' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), self.user_1.profile.id)

    def test_fill_profile_partial(self):
        """Test view for PATCH-update user profile"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Updated data
        data = {
            "first_name": "First name",
            "last_name": "Last name",
        }

        api_path = '%s:userprofile:profile' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.patch(reverse(api_path), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), self.user_1.profile.id)
        for field in data:
            self.assertEqual(response.data.get(field), data[field])

    def test_fill_profile(self):
        """Test view for PUT-update user profile"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Updated data
        data = {
            "first_name": "First name",
            "last_name": "Last name",
            "middle_name": "Middle name"
        }

        api_path = '%s:userprofile:profile' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.put(reverse(api_path), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), self.user_1.profile.id)
        for field in data:
            self.assertEqual(response.data.get(field), data[field])

    def test_error_fill_profile(self):
        """Test view for PUT-update user profile"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Updated data
        data = {
            "first_name": "First name",
            "last_name": "Last name",
        }

        api_path = '%s:userprofile:profile' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.put(reverse(api_path), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieving_profile_unauthorized_user(self):
        """Test view for retrieving unauthorized user profile"""

        api_path = '%s:userprofile:profile' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_cars(self):
        """Test view for getting list of users cars"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:car_list' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.cars_count)

    def test_car_detail(self):
        """Test view for getting detail of user car"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:car_detail' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path, kwargs={'pk': self.car_1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('user'), self.car_1.user.id)

