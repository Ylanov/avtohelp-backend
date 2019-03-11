from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from account import models as account_models
from catalog import models as catalog_models
from car import models as car_models
from order import models
from userprofile import models as profile_models


# Create your tests here.
class TestOrder(APITestCase):
    VERSION = settings.AVAILABLE_VERSIONS.get('current')

    @classmethod
    def setUpClass(cls):
        """Set up for class"""
        print(f"\nStart test order app v{cls.VERSION}")
        print("==========")

    @classmethod
    def tearDownClass(cls):
        """Tear down for class"""
        print("==========")
        print(f"End test order app v{cls.VERSION}\n")

    def setUp(self):
        # User data
        self.phone = '+79000000000'
        self.city = catalog_models.City.objects.create(name='Krasnodar')

        # Create car brands
        self.toyota = car_models.CarMark.objects.create(name='Toyota')

        # Create car models
        self.toyota_model = car_models.CarModel.objects.create(name='Supra',
                                                               mark=self.toyota)

        # Create car colors
        self.color_1 = car_models.CarColor.objects.create(name='White')

        # Create user
        self.user_1 = account_models.User.objects.make(phone='+79000000000', city=self.city)

        # Create user cars
        self.car_1 = car_models.Car.objects.create(mark=self.toyota,
                                                   car_model=self.toyota_model)
        self.car_user_1 = profile_models.ProfileCar.objects.create(owner=self.user_1,
                                                                   car=self.car_1,
                                                                   color=self.color_1,
                                                                   license_plate='aaa123aa 70')

        # Authorize
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_assistance_request(self):
        """Test create assurance request"""

        api_path = '%s:order:request-create' % self.VERSION
        data = {
            "issue": "Issue 1",
            "description": "Description",
            "geo_lat": "45.060487",
            "geo_lon": "38.944205",
            # "phone": "+79000000000"
        }
        response = self.client.post(reverse(api_path), data)
        assistance_request = models.AssistanceRequest.objects.first().id
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('id'), assistance_request)

    def test_list_created_assistance_requests(self):
        """
        Test list of created assurance requests
        Users: user_1, user_2, user_3
        Blacked users: user_2
        Assistance requests: AssistanceRequest(user_1),
                             AssistanceRequest(user_2),
                             AssistanceRequest(user_3)
        Result: [AssistanceRequest(user_1), AssistanceRequest(user_3),]
        """

        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = account_models.User.objects.make(phone='+79000000002', city=self.city)
        user_3 = account_models.User.objects.make(phone='+79000000003', city=self.city)

        # Create assistance requests
        models.AssistanceRequest.objects.create(user=self.user_1,
                                                issue='Issue 1',
                                                description='Description')
        models.AssistanceRequest.objects.create(user=user_2,
                                                issue='Issue 2',
                                                description='Description')
        models.AssistanceRequest.objects.create(user=user_3,
                                                issue='Issue 3',
                                                description='Description')

        # Put user_2 in BlackList
        profile_models.BlackList.objects.create(owner=self.user_1, foe=user_2)

        api_path = '%s:order:request-list' % self.VERSION

        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

    def test_detail_assistance_request(self):
        """Test detail of created assurance requests"""

        api_path = '%s:order:request-detail' % self.VERSION
        assistance_request = models.AssistanceRequest.objects.create(
            user=self.user_1,
            issue='Issue 1',
            description='Issue description'
        )
        response = self.client.get(reverse(api_path, kwargs={'pk': assistance_request.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
