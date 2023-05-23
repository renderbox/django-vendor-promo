from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase, Client
from django.urls import reverse
from vendor.models import CustomerProfile
from vendorpromo.models import CouponCode, PromotionalCampaign

User = get_user_model()


class CouponCodeModelTests(TestCase):

    fixtures = ['user', 'unit_test']

    def setUp(self):
        self.customer_profile = CustomerProfile.objects.get(pk=1)

    def test_coupon_code_create_fail(self):
        new_coupon_code = CouponCode()
        with self.assertRaises(Exception):
            new_coupon_code.save()

    def test_coupon_code_create_success(self):
        new_coupon_code = CouponCode()
        test_code = 'TESTCODE'
        new_coupon_code.code = test_code
        new_coupon_code.promo = PromotionalCampaign.objects.get(pk=1)
        new_coupon_code.max_redemptions = 2
        new_coupon_code.save()
        self.assertTrue(CouponCode.objects.get(code__icontains=test_code))


class CouponCodeViewTests(TestCase):

    fixtures = ['user', 'unit_test']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)
        self.customer_profile = CustomerProfile.objects.get(pk=1)

    def test_coupon_code_list_get_200(self):
        view_url = reverse('coupon-code-list')
        response = self.client.get(view_url)
        self.assertEquals(response.status_code, 200)

    def test_coupon_code_list_search_success(self):
        view_url = f"{reverse('coupon-code-list')}?search_filter=tom"
        response = self.client.get(view_url)
        self.assertIn("MORRELLOSALE", str(response.content))
        self.assertNotIn("JIMMYOFF", str(response.content))

    def test_coupon_code_list_search_empty(self):
        view_url = f"{reverse('coupon-code-list')}?search_filter=Peter"
        response = self.client.get(view_url)
        self.assertIn("No Coupon Codes", str(response.content))

    def test_coupon_code_create_get_200(self):
        view_url = reverse('coupon-code-create')
        response = self.client.get(view_url)
        self.assertEquals(response.status_code, 200)
    
    def test_coupon_code_create_post_success(self):
        view_url = reverse('coupon-code-create')
        post_data = {
            'code': "LED",
            'promo': 1,
            'max_redemptions': 3
        }
        response = self.client.post(view_url, post_data)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(CouponCode.objects.filter(code__icontains=post_data['code']))

    def test_coupon_code_update_get_200(self):
        coupon_code = CouponCode.objects.get(pk=1)
        view_url = reverse('coupon-code-update', kwargs={'uuid': coupon_code.uuid})
        response = self.client.get(view_url)
        self.assertEquals(response.status_code, 200)
    
    def test_coupon_code_update_post_success(self):
        coupon_code = CouponCode.objects.get(pk=1)
        view_url = reverse('coupon-code-update', kwargs={'uuid': coupon_code.uuid})
        post_data = {
            'max_redemptions': 33,
            'promo': 2,
            'code': "JIMMYOFF"
        }

        response = self.client.post(view_url, post_data)
        
        self.assertEqual(response.status_code, 302)
        coupon_code.refresh_from_db()
        self.assertEquals(coupon_code.max_redemptions, post_data['max_redemptions'])

    def test_delete_post_success(self):
        coupon_code = CouponCode.objects.get(pk=1)
        view_url = reverse('coupon-code-delete', kwargs={'uuid': coupon_code.uuid})
        response = self.client.post(view_url)
        self.assertEquals(response.status_code, 302)
        self.assertFalse(CouponCode.objects.filter(pk=1).exists())

    def test_delete_post_error(self):
        invalid_uuid = "5e90f83b-63a4-411d-91d4-842fc373f0a9"
        view_url = reverse('coupon-code-delete', kwargs={'uuid': invalid_uuid})
        response = self.client.post(view_url)
        self.assertEquals(response.status_code, 404)













