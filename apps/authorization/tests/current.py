from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from account.models import User
from authorization.models import SMSCode
from catalog.models import CarModel, CarMark, CarColor


class TestCatalog(TestCase):
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
        # user data
        self.phone = '+79000000000'

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

    def test_verification(self):
        """Test view for verify user phone"""

        data = {"phone": self.phone}

        api_path = '%s:authorization:verify' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path), data=data)
        sms_code = SMSCode.objects.filter(phone=data.get('phone')).first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sms_code.status, sms_code.SENT)

    def test_authorization(self):
        """Test view for authorize user"""

        # verify
        api_path = '%s:authorization:verify' % settings.AVAILABLE_VERSIONS.get('current')
        self.client.post(reverse(api_path), data={"phone": self.phone})
        sms_code = SMSCode.objects.filter(phone=self.phone).first()

        # authorize
        data = {"phone": self.phone, "code": int(sms_code.code)}
        api_path = '%s:authorization:auth' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path), data=data)
        sms_code = SMSCode.objects.filter(phone=self.phone).first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sms_code.status, sms_code.ACTIVATED)
