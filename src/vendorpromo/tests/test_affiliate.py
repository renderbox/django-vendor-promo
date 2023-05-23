from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse
from vendor.models import CustomerProfile
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

    def test_affiliate_create_fail_customer_profile_link(self):
        new_affiliate = Affiliate()
        new_affiliate.customer_profile = self.customer_profile
        with self.assertRaises(ValidationError):
            new_affiliate.save()

    def test_affiliate_create_success(self):
        new_affiliate = Affiliate()
        new_affiliate.customer_profile = CustomerProfile.objects.get(pk=2)
        new_affiliate.contact_name = "Peter Parker"
        new_affiliate.email = "jawa@mail.com"
        new_affiliate.company = "WML"
        new_affiliate.site = Site.objects.get(pk=1)
        new_affiliate.save()
        self.assertTrue(Affiliate.objects.get(customer_profile=self.customer_profile))

    def test_affiliate_create_except_customer_profile_success(self):
        contact_name = "Peter Parker"
        email = "jawa@mail.com"
        company = "WML"
        new_affiliate = Affiliate()
        new_affiliate.contact_name = contact_name
        new_affiliate.email = email
        new_affiliate.company = company
        new_affiliate.site = Site.objects.get(pk=1)
        new_affiliate.save()
        self.assertTrue(Affiliate.objects.get(contact_name=contact_name, email=email, company=company))

    def test_promo_create_only_customer_profile_success(self):
        new_affiliate = Affiliate()
        new_affiliate.customer_profile = CustomerProfile.objects.get(pk=2)
        new_affiliate.site = Site.objects.get(pk=1)
        new_affiliate.save()
        self.assertTrue(Affiliate.objects.get(customer_profile=self.customer_profile))

    def test_promo_create_only_contact_name_success(self):
        contact_name = "Peter Parker"
        new_affiliate = Affiliate()
        new_affiliate.contact_name = contact_name
        new_affiliate.site = Site.objects.get(pk=1)
        new_affiliate.save()
        self.assertTrue(Affiliate.objects.get(contact_name=contact_name))

    def test_promo_create_only_email_success(self):
        email = "jawa@mail.com"
        new_affiliate = Affiliate()
        new_affiliate.email = email
        new_affiliate.site = Site.objects.get(pk=1)
        new_affiliate.save()
        self.assertTrue(Affiliate.objects.get(email=email))

    def test_promo_create_only_company_success(self):
        company = "WML"
        new_affiliate = Affiliate()
        new_affiliate.company = company
        new_affiliate.site = Site.objects.get(pk=1)
        new_affiliate.save()
        self.assertTrue(Affiliate.objects.get(company=company))


class AffiliateViewTests(TestCase):

    fixtures = ['user', 'unit_test']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)
        self.existing_promo = Promo.objects.get(pk=1)
        self.customer_profile = CustomerProfile.objects.get(pk=1)

    def test_affiliate_list_get_200(self):
        view_url = reverse('affiliate-list')
        response = self.client.get(view_url)
        self.assertEquals(response.status_code, 200)

    def test_affiliate_list_search_success(self):
        view_url = f"{reverse('affiliate-list')}?search_filter=rob"
        response = self.client.get(view_url)
        self.assertIn("rob", str(response.content))
        self.assertNotIn("Norrin", str(response.content))

    def test_affiliate_list_search_empty(self):
        view_url = f"{reverse('affiliate-list')}?search_filter=Peter"
        response = self.client.get(view_url)
        self.assertIn("No Affiliates", str(response.content))

    def test_affiliate_create_get_200(self):
        view_url = reverse('affiliate-create')
        response = self.client.get(view_url)
        self.assertEquals(response.status_code, 200)
    
    def test_affiliate_create_post_success(self):
        view_url = reverse('affiliate-create')
        post_data = {
            'contact_name': "Peter Parker"
        }
        response = self.client.post(view_url, post_data)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(Affiliate.objects.filter(contact_name="Peter Parker"))

    def test_affiliate_create_post_error_empty_fields(self):
        view_url = reverse('affiliate-create')
        
        response = self.client.post(view_url, {})
        self.assertIn("You at least need to assign a Customer Profile or enter a Full Name, Email or Company for the Affiliate", str(response.content))

    def test_affiliate_create_post_error_customer_profile_link(self):
        view_url = reverse('affiliate-create')
        
        response = self.client.post(view_url, data={'customer_profile': 1})
        self.assertIn("The selected Customer Profile is already linked to an existing Affiliate.", str(response.content))

    def test_affiliate_update_get_200(self):
        affiliate = Affiliate.objects.get(pk=1)
        view_url = reverse('affiliate-update', kwargs={'uuid': affiliate.uuid})
        response = self.client.get(view_url)
        self.assertEquals(response.status_code, 200)
    
    def test_affiliate_update_post_success(self):
        affiliate = Affiliate.objects.get(pk=1)
        view_url = reverse('affiliate-update', kwargs={'uuid': affiliate.uuid})
        post_data = {
            'company': 'NXP'
        }

        response = self.client.post(view_url, post_data)
        
        self.assertEqual(response.status_code, 302)
        affiliate.refresh_from_db()
        self.assertEquals(affiliate.company, post_data['company'])

    def test_affiliate_update_post_error(self):
        affiliate = Affiliate.objects.get(pk=2)
        view_url = reverse('affiliate-update', kwargs={'uuid': affiliate.uuid})
        post_data = {
            'customer_profile': 1
        }
        
        response = self.client.post(view_url, post_data)

        self.assertIn("The selected Customer Profile is already linked to an existing Affiliate.", str(response.content))

    def test_delete_post_success(self):
        affiliate = Affiliate.objects.get(pk=1)
        view_url = reverse('affiliate-delete', kwargs={'uuid': affiliate.uuid})
        response = self.client.post(view_url)
        self.assertEquals(response.status_code, 302)
        self.assertFalse(Affiliate.objects.filter(pk=1).exists())

    def test_delete_post_error(self):
        invalid_uuid = "5e90f83b-63a4-411d-91d4-842fc373f0a9"
        view_url = reverse('affiliate-delete', kwargs={'uuid': invalid_uuid})
        response = self.client.post(view_url)
        self.assertEquals(response.status_code, 302)













