from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse

from vendor.models import Offer
from vendorpromo.models import Promo

User = get_user_model()


class PromoModelTests(TestCase):

    fixtures = ['user', 'unit_test']

    def setUp(self):
        self.existing_promo = Promo.objects.get(pk=1)
        self.offer_site_1 = Offer.objects.get(pk=1)
        self.offer_site_2 = Offer.objects.get(pk=2)

    def test_promo_create_success(self):
        promo = Promo()
        code = "NEW-PROMO"
        promo.code = "NEW-PROMO"
        promo.offer = self.offer_site_1
        self.assertFalse(Promo.objects.filter(code=code, offer__site__pk=1).exists())
        promo.save()
        self.assertTrue(Promo.objects.filter(code=code, offer__site__pk=1).exists())

    def test_promo_create_duplicate_code_same_site_error(self):
        promo = Promo()
        promo.code = self.existing_promo.code
        promo.offer = self.offer_site_1
        with self.assertRaises(ValidationError):
            promo.save()

    def test_promo_create_duplicate_code_same_site_success(self):
        promo = Promo()
        promo.code = self.existing_promo.code
        promo.offer = self.offer_site_2
        self.assertFalse(Promo.objects.filter(code=self.existing_promo.code, offer__site__pk=2).exists())
        promo.save()
        self.assertTrue(Promo.objects.filter(code=self.existing_promo.code, offer__site__pk=2).exists())


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
        view_url = reverse('vendorpromo-update', kwargs={'uuid': Promo.objects.all().first().uuid})
        response = self.client.get(view_url)
        self.assertEquals(response.status_code, 200)

    def test_promo_list_view_200(self):
        view_url = reverse('vendorpromo-list')
        response = self.client.get(view_url)
        self.assertEquals(response.status_code, 200)
