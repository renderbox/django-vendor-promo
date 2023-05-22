from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse
from vendor.models import CustomerProfile, Offer
from vendor.models.base import get_product_model
from vendorpromo.models import PromotionalCampaign, Affiliate

User = get_user_model()


class PromotionalCampaignModelTests(TestCase):

    fixtures = ['user', 'unit_test']

    def setUp(self):
        self.existing_promo = PromotionalCampaign.objects.get(pk=1)
        self.customer_profile = CustomerProfile.objects.get(pk=1)

    def test_promotional_campaign_create_fail(self):
        new_promotional_campaign = PromotionalCampaign()
        with self.assertRaises(Exception):
            new_promotional_campaign.save()

    def test_promotional_campaign_create_success(self):
        site = Site.objects.get(pk=1)
        offer = Offer.objects.get(pk=1)
        new_promotional_campaign = PromotionalCampaign()
        new_promotional_campaign.max_redemptions = 10
        new_promotional_campaign.site = site
        new_promotional_campaign.applies_to = Offer.objects.get(pk=1)
        new_promotional_campaign.save()
        self.assertTrue(PromotionalCampaign.objects.get(site=site, applies_to=offer))


class PromotionalCampaignViewTests(TestCase):

    fixtures = ['user', 'unit_test']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)
        self.existing_promo = PromotionalCampaign.objects.get(pk=1)
        self.customer_profile = CustomerProfile.objects.get(pk=1)

    def test_promotional_campaign_list_get_200(self):
        view_url = reverse('promotional-campaign-list')
        response = self.client.get(view_url)
        self.assertEquals(response.status_code, 200)

    def test_promotional_campaign_list_search_success(self):
        view_url = f"{reverse('promotional-campaign-list')}?search_filter=tom"
        response = self.client.get(view_url)
        self.assertIn("Tom", str(response.content))
        self.assertNotIn("Jimmy", str(response.content))

    def test_promotional_campaign_list_search_empty(self):
        view_url = f"{reverse('promotional-campaign-list')}?search_filter=Peter"
        response = self.client.get(view_url)
        self.assertIn("No Promotional Campaigns", str(response.content))

    def test_promotional_campaign_create_get_200(self):
        view_url = reverse('promotional-campaign-create')
        response = self.client.get(view_url)
        self.assertEquals(response.status_code, 200)
    
    def test_promotional_campaign_create_post_success(self):
        view_url = reverse('promotional-campaign-create')
        post_data = {
            'name': "Peter Townsend",
            'max_redemptions': 10,
            'applies_to': [1],
            'site': 1,
            'is_percent_off': False,
            'discount_value': 10
        }
        response = self.client.post(view_url, post_data)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(Offer.objects.filter(name='Peter Townsend').exists())
        self.assertEqual(Offer.objects.get(name='Peter Townsend').products.first(), get_product_model().objects.get(pk=1))
        self.assertTrue(PromotionalCampaign.objects.filter(name="Peter Townsend"))
        self.assertEqual(Offer.objects.get(name="Peter Townsend").prices.first().cost, -post_data['discount_value'])

    def test_promotional_campaign_update_get_200(self):
        promotional_campaign = PromotionalCampaign.objects.get(pk=1)
        view_url = reverse('promotional-campaign-update', kwargs={'uuid': promotional_campaign.uuid})
        response = self.client.get(view_url)
        self.assertEquals(response.status_code, 200)
    
    def test_promotional_campaign_update_post_success(self):
        offer_counter = Offer.objects.all().count()
        applies_to_offer = Offer.objects.get(pk=7)
        promotional_campaign = PromotionalCampaign.objects.get(pk=1)
        view_url = reverse('promotional-campaign-update', kwargs={'uuid': promotional_campaign.uuid})
        post_data = {
            'name': 'NXP',
            'is_percent_off': True,
            'discount_value': 13
        }

        response = self.client.post(view_url, post_data)
        
        self.assertEqual(response.status_code, 302)
        promotional_campaign.refresh_from_db()
        applies_to_offer.refresh_from_db()
        self.assertEquals(promotional_campaign.name, post_data['name'])
        self.assertEquals(promotional_campaign.name, applies_to_offer.name)
        self.assertEquals(post_data['discount_value'], applies_to_offer.prices.first().cost)
        self.assertEquals(offer_counter, Offer.objects.all().count())
    
    def test_promotional_campaign_update_post_discount_value_error(self):
        promotional_campaign = PromotionalCampaign.objects.get(pk=1)
        view_url = reverse('promotional-campaign-update', kwargs={'uuid': promotional_campaign.uuid})
        post_data = {
            'name': 'NXP',
            'is_percent_off': False,
            'discount_value': 0
        }

        response = self.client.post(view_url, post_data)
        
        self.assertIn("Number must be greater than 0", str(response.content))
    
    def test_promotional_campaign_update_post_percent_error(self):
        promotional_campaign = PromotionalCampaign.objects.get(pk=1)
        view_url = reverse('promotional-campaign-update', kwargs={'uuid': promotional_campaign.uuid})
        post_data = {
            'name': 'NXP',
            'is_percent_off': True,
            'discount_value': 120
        }

        response = self.client.post(view_url, post_data)
        
        self.assertIn("Must be a number between 1 and 99", str(response.content))

    def test_delete_post_success(self):
        promotional_campaign = PromotionalCampaign.objects.get(pk=1)
        view_url = reverse('promotional-campaign-delete', kwargs={'uuid': promotional_campaign.uuid})
        response = self.client.post(view_url)
        self.assertEquals(response.status_code, 302)
        self.assertFalse(PromotionalCampaign.objects.filter(pk=1).exists())

    def test_delete_post_error(self):
        invalid_uuid = "5e90f83b-63a4-411d-91d4-842fc373f0a9"
        view_url = reverse('promotional-campaign-delete', kwargs={'uuid': invalid_uuid})
        response = self.client.post(view_url)
        self.assertEquals(response.status_code, 404)













