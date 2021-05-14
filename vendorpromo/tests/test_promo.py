from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from vendorpromo.models import Promo

User = get_user_model()


class PromoModelTests(TestCase):

    def setUp(self):
        self.existing_promo = Promo.objects.get(pk=1)

    def test_offer_create_success(self):
        raise NotImplementedError

    def test_offer_create_offer_error(self):
        raise NotImplementedError

    def test_offer_update_success(self):
        raise NotImplementedError


class PromoViewTests(TestCase):

    fixtures = ['user', 'unit_test']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)

    def test_promo_create_view_200(self):
        view_url = reverse('vendorpromo-create')
        response = self.client.get(view_url)
        self.assertEquals(response.status_code, 200)

    def test_promo_update_view_200(self):
        view_url = reverse('vendorpromo-update')
        response = self.client.get(view_url)
        self.assertEquals(response.status_code, 200)

    def test_promo_list_view_200(self):
        view_url = reverse('vendorpromo-list')
        response = self.client.get(view_url)
        self.assertEquals(response.status_code, 200)
