from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse

from vendor.models import CustomerProfile, Offer
from vendorpromo.models import Promo, Affiliate

User = get_user_model()


class AffiliateModelTests(TestCase):

    fixtures = ['user', 'unit_test']

    def setUp(self):
        self.existing_promo = Promo.objects.get(pk=1)
        self.customer_profile = CustomerProfile.objects.get(pk=1)

    def test_affiliate_create_fail(self):
        new_affiliate = Affiliate()
        with self.assertRaises(ValidationError):
            new_affiliate.save()

    def test_affiliate_create_success(self):
        new_affiliate = Affiliate()
        new_affiliate.customer_profile = self.customer_profile
        new_affiliate.full_name = "Norrin Radd"
        new_affiliate.email = "jawa@mail.com"
        new_affiliate.company = "WML"
        new_affiliate.save()
        self.assertTrue(Affiliate.objects.get(customer_profile=self.customer_profile))

    def test_affiliate_create_except_customer_profile_success(self):
        full_name = "Norrin Radd"
        email = "jawa@mail.com"
        company = "WML"
        new_affiliate = Affiliate()
        new_affiliate.full_name = full_name
        new_affiliate.email = email
        new_affiliate.company = company
        new_affiliate.save()
        self.assertTrue(Affiliate.objects.get(full_name=full_name, email=email, company=company))

    def test_promo_create_only_customer_profile_success(self):
        new_affiliate = Affiliate()
        new_affiliate.customer_profile = self.customer_profile
        new_affiliate.save()
        self.assertTrue(Affiliate.objects.get(customer_profile=self.customer_profile))

    def test_promo_create_only_full_name_success(self):
        full_name = "Norrin Radd"
        new_affiliate = Affiliate()
        new_affiliate.full_name = full_name
        new_affiliate.save()
        self.assertTrue(Affiliate.objects.get(full_name=full_name))

    def test_promo_create_only_email_success(self):
        email = "jawa@mail.com"
        new_affiliate = Affiliate()
        new_affiliate.email = email
        new_affiliate.save()
        self.assertTrue(Affiliate.objects.get(email=email))

    def test_promo_create_only_company_success(self):
        company = "WML"
        new_affiliate = Affiliate()
        new_affiliate.company = company
        new_affiliate.save()
        self.assertTrue(Affiliate.objects.get(company=company))


# class PromoViewTests(TestCase):

#     fixtures = ['user', 'unit_test']

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.get(pk=1)
#         self.client.force_login(self.user)

#     def test_promo_create_view_200(self):
#         view_url = reverse('vendorpromo-create')
#         response = self.client.get(view_url)
#         self.assertEquals(response.status_code, 200)

#     def test_promo_update_view_200(self):
#         view_url = reverse('vendorpromo-update', kwargs={'uuid': Promo.objects.all().first().uuid})
#         response = self.client.get(view_url)
#         self.assertEquals(response.status_code, 200)

#     def test_promo_list_view_200(self):
#         view_url = reverse('vendorpromo-list')
#         response = self.client.get(view_url)
        # self.assertEquals(response.status_code, 200)
