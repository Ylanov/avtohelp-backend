from django.conf import settings
from django.urls import reverse
from django.contrib.gis.geos import Point
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from account import models as account_models
from catalog import models as catalog_models
from car import models as car_models
from base import models as base_models
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
        self.user_1 = account_models.User.objects.make(phone='+79000000000')
        self.user_2 = account_models.User.objects.make(phone='+79000000002')
        self.user_3 = account_models.User.objects.make(phone='+79000000003')

        # Create devices
        self.device_1 = profile_models.FCMDevice.objects.create(user=self.user_1, active=True)
        self.device_2 = profile_models.FCMDevice.objects.create(user=self.user_2, active=True)
        self.device_3 = profile_models.FCMDevice.objects.create(user=self.user_3, active=True)

        # Create assistance requests
        models.AssistanceRequest.objects.create(user=self.user_1,
                                                issue='Issue 1',
                                                description='Description',
                                                location=Point(45.061016, 38.944007, srid=4326))
        self.assistance_request_1 = models.AssistanceRequest.objects.create(user=self.user_2,
                                                                            issue='Issue 2',
                                                                            description='Description',
                                                                            location=Point(55.062003, 28.940738, srid=4326))
        models.AssistanceRequest.objects.create(user=self.user_3,
                                                issue='Issue 3',
                                                description='Description',
                                                location=Point(65.062003, 18.940738, srid=4326))

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
            "contact_phone": "+79000000000",
            "text_address": "улица Новицкого 2/4, возле ТЦ Boss House"
        }
        response = self.client.post(reverse(api_path), data)
        assistance_request = models.AssistanceRequest.objects.last().id
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
        # Put user_2 in BlackList
        profile_models.BlackList.objects.create(owner=self.user_1, foe=self.user_2)

        api_path = '%s:order:request-list' % self.VERSION

        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_service_list_query(self):
        """Test service list query - from center & position"""
        query = {
            'position': ['45.061016, 38.944007']  # latitude, longitude
        }
        api_path = '%s:order:request-list' % self.VERSION
        response = self.client.get(reverse(api_path), data=query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_service_list_query_1(self):
        """Test service list query - filter by distance"""
        query = {
            'coordinates': ['55.062003, 28.940738'],  # latitude, longitude
        }
        api_path = '%s:order:request-list' % self.VERSION
        response = self.client.get(reverse(api_path), data=query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0].get('distance'), 0.0)  # output in meters

    def test_service_list_query_2(self):
        """Test service list query - filter by profile id"""
        query = {
            'profile_id': self.assistance_request_1.user.profile.id
        }
        api_path = '%s:order:request-list' % self.VERSION
        response = self.client.get(reverse(api_path), data=query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0].get('profile_id'), self.assistance_request_1.user.profile.id)

    def test_service_list_query_3(self):
        """Test service list query - filter by distance"""
        query = {
            'coordinates': ['55.062003, 28.940738, 100000000'],  # latitude, longitude
        }
        api_path = '%s:order:request-list' % self.VERSION
        response = self.client.get(reverse(api_path), data=query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[1].get('distance'), 0.0)  # output in meters
        self.assertEqual(response.data[2].get('distance'), 1504877.55296152)  # output in meters

    def test_count_created_assistance_requests(self):
        """
        Test count of created assurance requests
        Users: user_1, user_2, user_3
        Blacked users: user_2
        Assistance requests: AssistanceRequest(user_1),
                             AssistanceRequest(user_2),
                             AssistanceRequest(user_3)
        Result: {"count": 2}

        """

        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Put user_2 in BlackList
        profile_models.BlackList.objects.create(owner=self.user_1, foe=self.user_2)

        api_path = '%s:order:requests-count' % self.VERSION

        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'),
                         models.AssistanceRequest.objects.available(user=self.user_1).count())

    def test_detail_assistance_request(self):
        """Test detail of created assurance requests"""

        api_path = '%s:order:request-detail' % self.VERSION
        assistance_request = models.AssistanceRequest.objects.create(
            user=self.user_1,
            issue='Issue 1',
            description='Issue description'
        )
        response = self.client.get(reverse(api_path, kwargs={'pk': assistance_request.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sent_notification_by_distance_and_location_relevance(self):
        """Test sent notification by distance and location relevance"""
        self.user_2.profilelocation.location = Point(x=45.04934, y=38.960508, srid=4326)
        self.user_2.profilelocation.save()
        assistance_request = models.AssistanceRequest.objects.create(user=self.user_2,
                                                                     issue='Issue 1',
                                                                     description='Description',
                                                                     location=Point(45.05934, 38.960508, srid=4326))
        singleton = base_models.PushNotificationConfiguration.get_solo()
        devices = profile_models.FCMDevice.objects.filter(active=True) \
            .annotate_device_geo_position_relevance() \
            .filter(geo_position_is_valid=True) \
            .annotate_device_distance_from_assistance_request(assistance_request=assistance_request) \
            .filter(distance__lte=singleton.radius)
        self.assertEqual(devices.count(), 1)

    # def test_update_assistance_request(self):
    #     """Test update of created assurance requests"""
    #
    #     api_path = '%s:order:request-update' % self.VERSION
    #     assistance_request = models.AssistanceRequest.objects.create(
    #         user=self.user_1,
    #         issue='Issue 1',
    #         description='Issue description'
    #     )
    #     response = self.client.patch(reverse(api_path, kwargs={'pk': assistance_request.pk}),
    #                                  data={'status': models.AssistanceRequest.EXPIRED})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data.get('status'), models.AssistanceRequest.EXPIRED)

    # def test_update_assistance_request_1(self):
    #     """Test wrong update of created assurance requests"""
    #
    #     api_path = '%s:order:request-update' % self.VERSION
    #     assistance_request = models.AssistanceRequest.objects.create(
    #         user=self.user_1,
    #         issue='Issue 1',
    #         description='Issue description'
    #     )
    #     response = self.client.patch(reverse(api_path, kwargs={'pk': assistance_request.pk}),
    #                                  data={'status': 9999})
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_delete_assistance_request(self):
    #     """Test delete created assurance requests"""
    #
    #     api_path = '%s:order:request-delete' % self.VERSION
    #     assistance_request = models.AssistanceRequest.objects.create(
    #         user=self.user_1,
    #         issue='Issue 1',
    #         description='Issue description'
    #     )
    #     response = self.client.delete(reverse(api_path, kwargs={'pk': assistance_request.id}))
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # def test_delete_assistance_request_1(self):
    #     """Test wrong delete created assurance requests"""
    #
    #     api_path = '%s:order:request-delete' % self.VERSION
    #     models.AssistanceRequest.objects.create(
    #         user=self.user_1,
    #         issue='Issue 1',
    #         description='Issue description'
    #     )
    #     response = self.client.delete(reverse(api_path, kwargs={'pk': 420}))
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
