from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from autofixture import AutoFixture

from base import models
from account import models as account_models
from catalog import models as catalog_models

from django.contrib.gis.geos import Point


class TestCatalog(APITestCase):
    VERSION = settings.AVAILABLE_VERSIONS.get('current')

    @classmethod
    def setUpClass(cls):
        """Set up for class"""
        print(f"\nStart test base app v{cls.VERSION}")
        print("==========")

    @classmethod
    def tearDownClass(cls):
        """Tear down for class"""
        print("==========")
        print(f"End test base app v{cls.VERSION}\n")

    def setUp(self):
        # Create Service Category
        self.service_cat_1 = catalog_models.ServiceCategory.objects.create(name='Category 1')
        self.service_cat_2 = catalog_models.ServiceCategory.objects.create(name='Category 2')

        # Create service
        self.service_1 = models.Service.objects.create(category=self.service_cat_1,
                                                       description='Description',
                                                       phone='+79112223344',
                                                       location=Point(1.00000, 2.0000))
        self.service_2 = models.Service.objects.create(category=self.service_cat_2,
                                                       description='Description',
                                                       phone='+79998887766',
                                                       location=Point(1.00000, 3.0000))

        # Create City
        self.city = catalog_models.City.objects.create(name='City 1')

        # Create user
        self.user = account_models.User.objects.make(phone='+79000000000',
                                                     city=self.city)

        # Create PushNotifications
        self.notification = models.PushNotification.objects.create(title='Push 1',
                                                                   description='Description',
                                                                   user=self.user)

    def test_news_list(self):
        """Test news list view"""

        # Create news
        AutoFixture(models.Newsletter).create(5)

        api_path = '%s:base:news-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), models.Newsletter.objects.count())

    def test_news_detail(self):
        """Test news detail view"""

        # Create news
        news = AutoFixture(models.Newsletter).create(5)

        api_path = '%s:base:news-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': news[0].id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notifications_list(self):
        """Test notifications list view"""

        api_path = '%s:base:notifications-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), models.PushNotification.objects.count())

    def test_notifications_detail(self):
        """Test notifications detail view"""

        api_path = '%s:base:notifications-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': self.notification.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_services_list(self):
        """Test services list view"""

        api_path = '%s:base:service-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), models.Service.objects.count())

    def test_services_detail(self):
        """Test services detail view"""

        api_path = '%s:base:service-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': self.service_2.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
