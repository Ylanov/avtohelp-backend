from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from account.models import User
from catalog.models import City


class TestCatalog(APITestCase):
    VERSION = settings.AVAILABLE_VERSIONS.get("current")

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
        # Create cities
        self.city_1 = City.objects.create(name="Krasnodar")
        self.city_2 = City.objects.create(name="Kaliningrad")
        self.city_3 = City.objects.create(name="Novosibirsk")
        self.cities_count = City.objects.count()

    def test_list_cities(self):
        """Test view for getting list of cities"""
        api_path = "%s:catalog:city-list" % settings.AVAILABLE_VERSIONS.get(
            "current"
        )
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.cities_count)

    def test_city_detail(self):
        """Test view for getting detail of city"""
        api_path = "%s:catalog:city-detail" % settings.AVAILABLE_VERSIONS.get(
            "current"
        )
        response = self.client.get(
            reverse(api_path, kwargs={"pk": self.city_1.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
