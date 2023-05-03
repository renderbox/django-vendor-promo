
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase

from unittest import skipIf

from vendor.models import Offer
from vendor.models.utils import random_string

from vendorpromo.config import VENDOR_PROMO_PROCESSOR
from vendorpromo.forms import PromoForm
from vendorpromo.models import Promo
from vendorpromo.processors.vouchery import VoucheryProcessor

User = get_user_model()


class BaseProcessorTests(TestCase):

    fixtures = ['user', 'unit_test']

    def setUp(self):
        pass

    # def test_create_promo_success(self):
    #     raise NotImplementedError

    # def test_create_promo_fail(self):
    #     raise NotImplementedError

    # def test_update_promo_success(self):
    #     raise NotImplementedError

    # def test_update_promo_fail(self):
    #     raise NotImplementedError

    # def test_delete_promo_success(self):
    #     raise NotImplementedError

    # def test_delete_promo_fail(self):
    #     raise NotImplementedError

    # def test_is_code_valid_success(self):
    #     raise NotImplementedError

    # def test_is_code_valid_fail(self):
    #     raise NotImplementedError

    # def test_redeem_code_success(self):
    #     raise NotImplementedError

    # def test_redeem_code_fail(self):
    #     raise NotImplementedError

    # def test_confirm_redeemed_code_success(self):
    #     raise NotImplementedError

    # def test_confirm_redeemed_code_fail(self):
    #     raise NotImplementedError

    # def test_process_promo_success(self):
    #     raise NotImplementedError

    # def test_process_promo_fail(self):
    #     raise NotImplementedError


@skipIf(VENDOR_PROMO_PROCESSOR != "vouchery.VoucheryProcessor", "VoucheryPromoProcessor not set")
class VoucheryProcessorTests(TestCase):

    fixtures = ['user', 'unit_test']

    TEAM = "Whitemoon Dreams"

    def setUp(self):
        self.existing_campaigns = None
        self.promo_processor = VoucheryProcessor
        processor = self.promo_processor(Site.objects.get(pk=1))
        processor.get_campaigns(**{'team_eq': self.TEAM})
        if processor.response_content:
            self.existing_campaigns = [{'id': campaign['id'], 'name': campaign['name']} for campaign in processor.response_content]

    # Utils
    # def test_check_response_success(self, response):
    #     raise NotImplementedError

    # def test_check_response_fail(self, response):
    #     raise NotImplementedError

    # def test_get_headers_success(self):
    #     raise NotImplementedError

    # def test_get_headers_fail(self):
    #     raise NotImplementedError

    ############################
    # VOUCHERY API CALLS

    #############
    # Campaigns
    def test_create_campaign_success(self):
        campaign_name = "Django Vendor Promo Campaign"
        processor = self.promo_processor(Site.objects.get(pk=1))
        extra_params = {
            "type": "MainCampaign",
            "template": "discount",
            'team': self.TEAM
        }

        if self.existing_campaigns:
            if campaign_name in [campaign['name'] for campaign in self.existing_campaigns]:
                campaign_id = next([campaign['id'] for campaign in self.existing_campaigns if campaign['name'] == campaign_name], None)
                processor.delete_campaign(campaign_id)
                processor.clear_response_variables()

        processor.create_campaign(campaign_name, **extra_params)
        self.assertTrue(processor.is_request_success)
        self.assertIn("id", processor.response_content)
        processor.delete_campaign(processor.response_content['id'])

    def test_create_campaign_additional_params_success(self):
        campaign_name = "Django Vendor Promo Campaign Description"
        description = 'Testing adding params'
        processor = self.promo_processor(Site.objects.get(pk=1))
        extra_params = {
            "type": "MainCampaign",
            "template": "discount",
            'description': description,
            'team': self.TEAM
        }

        if self.existing_campaigns:
            if campaign_name in [campaign['name'] for campaign in self.existing_campaigns]:
                campaign_id = next([campaign['id'] for campaign in self.existing_campaigns if campaign['name'] == campaign_name])
                processor.delete_campaign(campaign_id)
                processor.clear_response_variables()

        processor.create_campaign(campaign_name, **extra_params)
        self.assertTrue(processor.is_request_success)
        self.assertIn("id", processor.response_content)
        self.assertEquals(description, processor.response_content['description'])
        processor.delete_campaign(processor.response_content['id'])

    def test_create_campaign_existing_name_fail(self):
        processor = self.promo_processor(Site.objects.get(pk=1))
        extra_params = {
            "type": "MainCampaign",
            "template": "discount",
            'team': self.TEAM
        }

        if not self.existing_campaigns:
            campaign_name = "Django Vendor Promo Campaign"
            extra_params = {"type": "MainCampaign", "template": "discount", 'team': self.TEAM}
            processor.create_campaign(campaign_name, **extra_params)
            processor.clear_response_variables()
        else:
            campaign_name = self.existing_campaigns[0]['name']

        processor.create_campaign(campaign_name, **extra_params)
        self.assertFalse(processor.is_request_success)

    def test_get_campaign_success(self):
        campaign_name = "Test Get Campaign"
        campaign_id = None
        extra_params = {
            "type": "MainCampaign",
            "template": "discount",
            'team': self.TEAM
        }

        if not self.existing_campaigns:
            create_processor = self.promo_processor(Site.objects.get(pk=1))
            create_processor.create_campaign(campaign_name, **extra_params)
            campaign_id = create_processor.response_content['id']
        else:
            campaign_id = self.existing_campaigns[0]['id']
            campaign_name = self.existing_campaigns[0]['name']

        processor = self.promo_processor(Site.objects.get(pk=1))
        processor.get_campaign(campaign_id)
        self.assertTrue(processor.is_request_success)
        self.assertEquals(campaign_name, processor.response_content['name'])

    def test_get_campaign_fail(self):
        processor = self.promo_processor(Site.objects.get(pk=1))
        processor.get_campaign(-2)
        self.assertFalse(processor.is_request_success)

    def test_update_campaign_success(self):
        campaign_name = "Test Updateing Campaign"
        campaign_id = None
        update_value = {"description": "Update campaign works"}
        extra_params = {
            "type": "MainCampaign",
            "template": "discount",
            "team": self.TEAM
        }

        if not self.existing_campaigns:
            create_processor = self.promo_processor(Site.objects.get(pk=1))
            create_processor.create_campaign(campaign_name, **extra_params)
            campaign_id = create_processor.response_content['id']
        else:
            campaign_name = self.existing_campaigns[0]['name']
            campaign_id = self.existing_campaigns[0]['id']

        processor = self.promo_processor(Site.objects.get(pk=1))
        processor.update_campaign(campaign_id, **update_value)
        self.assertTrue(processor.is_request_success)
        processor.clear_response_variables()
        processor.get_campaign(campaign_id)
        self.assertEquals(update_value['description'], processor.response_content['description'])

    def test_update_campaign_fail(self):
        processor = self.promo_processor(Site.objects.get(pk=1))
        processor.update_campaign(-2, **{"type": "MainCampaign"})
        self.assertFalse(processor.is_request_success)

    def test_delete_campaign_success(self):
        campaign_params = {
            "type": "MainCampaign",
            "template": "discount",
            'team': self.TEAM
        }
        create_processor = self.promo_processor(Site.objects.get(pk=1))
        create_processor.create_campaign(random_string(), **campaign_params)
        campaign_id = create_processor.response_content['id']

        processor = self.promo_processor(Site.objects.get(pk=1))
        processor.delete_campaign(campaign_id)
        self.assertTrue(processor.is_request_success)

    def test_delete_campaign_fail(self):
        processor = self.promo_processor(Site.objects.get(pk=1))
        processor.delete_campaign(-2)
        self.assertFalse(processor.is_request_success)

    # def test_delete_full_campaign_success(self):
    #     campaing_ids = []
    #     processor = self.promo_processor(Site.objects.get(pk=1))

    #     for campaign_id in campaing_ids:
    #         processor.delete_full_campaign(campaign_id)

    #     self.assertTrue(processor.is_request_success)

    #############
    # Reward
    def test_create_reward_success(self):
        campaign_name = random_string()
        campaign_id = None
        sub_campaign_name = random_string()
        sub_campaign_id = None
        reward_id = None
        processor = self.promo_processor(Site.objects.get(pk=1))
        campaign_params = {
            "type": "MainCampaign",
            "template": "discount",
            "team": self.TEAM,
            "status": "active"
        }
        sub_campaign_params = {
            "type": "SubCampaign",
            "template": "sub_redemption",
            "voucher_type": "generic",
            "triggers_on": "redemption",
            "status": "active"
        }
        reward_params = {
            "type": "SetDiscount",
            "discount_type": "percentage",
            "discount_value": 15
        }

        processor.create_campaign(campaign_name, **campaign_params)
        campaign_id = processor.response_content['id']
        processor.clear_response_variables()
        sub_campaign_params["parent_id"] = campaign_id
        processor.create_campaign(sub_campaign_name, **sub_campaign_params)
        sub_campaign_id = processor.response_content['id']
        processor.clear_response_variables()
        processor.create_reward(sub_campaign_id, **reward_params)
        reward_id = processor.response_content['id']

        processor.get_reward(reward_id)
        self.assertTrue(processor.is_request_success)
        self.assertGreater(len(processor.response_content), 0)

        processor.delete_reward(reward_id)
        processor.delete_campaign(sub_campaign_id)
        processor.delete_campaign(campaign_id)

    def test_create_reward_fail(self):
        processor = self.promo_processor(Site.objects.get(pk=1))
        processor.create_reward(-2)
        self.assertFalse(processor.is_request_success)

    def test_get_reward_success(self):
        campaign_name = random_string()
        campaign_id = None
        sub_campaign_name = random_string()
        sub_campaign_id = None
        voucher_code = random_string(length=5, check=[campaign_name, sub_campaign_name])
        reward_id = None
        processor = self.promo_processor(Site.objects.get(pk=1))
        campaign_params = {
            "type": "MainCampaign",
            "template": "discount",
            "team": self.TEAM,
            "status": "active"
        }
        sub_campaign_params = {
            "type": "SubCampaign",
            "template": "sub_redemption",
            "voucher_type": "generic",
            "triggers_on": "redemption",
            "status": "active"
        }
        reward_params = {
            "type": "SetDiscount",
            "discount_type": "percentage",
            "discount_value": 15
        }

        processor.create_campaign(campaign_name, **campaign_params)
        campaign_id = processor.response_content['id']
        processor.clear_response_variables()
        sub_campaign_params["parent_id"] = campaign_id
        processor.create_campaign(sub_campaign_name, **sub_campaign_params)
        sub_campaign_id = processor.response_content['id']
        processor.clear_response_variables()
        processor.create_reward(sub_campaign_id, **reward_params)
        reward_id = processor.response_content['id']
        processor.clear_response_variables()
        processor.create_voucher(voucher_code, campaign_id)
        processor.clear_response_variables()

        processor.get_reward(reward_id)
        self.assertTrue(processor.is_request_success)
        self.assertGreater(len(processor.response_content), 0)

        processor.delete_voucher(voucher_code)
        processor.delete_reward(reward_id)
        processor.delete_campaign(sub_campaign_id)
        processor.delete_campaign(campaign_id)

    def test_get_reward_fail(self):
        processor = self.promo_processor(Site.objects.get(pk=1))
        processor.get_reward(-2)
        self.assertFalse(processor.is_request_success)

    # def test_update_reward_success(self):
    #     raise NotImplementedError

    # def test_update_reward_fail(self):
    #     raise NotImplementedError

    # def test_delete_reward_success(self):
    #     raise NotImplementedError

    # def test_delete_reward_fail(self):
    #     raise NotImplementedError

    #############
    # Voucher
    def test_create_voucher_success(self):
        campaign_name = random_string()
        campaign_id = None
        sub_campaign_name = random_string()
        sub_campaign_id = None
        voucher_code = random_string(length=5, check=[campaign_name, sub_campaign_name])
        reward_id = None
        processor = self.promo_processor(Site.objects.get(pk=1))
        campaign_params = {
            "type": "MainCampaign",
            "template": "discount",
            "team": self.TEAM,
            "status": "active"
        }
        sub_campaign_params = {
            "type": "SubCampaign",
            "template": "sub_redemption",
            "voucher_type": "generic",
            "triggers_on": "redemption",
            "status": "active"
        }
        reward_params = {
            "type": "SetDiscount",
            "discount_type": "percentage",
            "discount_value": 15
        }

        processor.create_campaign(campaign_name, **campaign_params)
        campaign_id = processor.response_content['id']
        processor.clear_response_variables()
        sub_campaign_params["parent_id"] = campaign_id
        processor.create_campaign(sub_campaign_name, **sub_campaign_params)
        sub_campaign_id = processor.response_content['id']
        processor.clear_response_variables()
        processor.create_reward(sub_campaign_id, **reward_params)
        reward_id = processor.response_content['id']
        processor.clear_response_variables()
        processor.create_voucher(voucher_code, sub_campaign_id)

        self.assertTrue(processor.is_request_success)
        self.assertIn('id', processor.response_content)

        processor.delete_voucher(voucher_code)
        processor.delete_reward(reward_id)
        processor.delete_campaign(sub_campaign_id)
        processor.delete_campaign(campaign_id)

    def test_create_voucher_fail(self):
        processor = self.promo_processor(Site.objects.get(pk=1))
        processor.create_voucher(random_string(), -2)
        self.assertFalse(processor.is_request_success)

    def test_get_vouchers_success(self):
        campaign_name = random_string()
        campaign_id = None
        sub_campaign_name = random_string()
        sub_campaign_id = None
        voucher_code = random_string(length=5, check=[campaign_name, sub_campaign_name])
        reward_id = None
        processor = self.promo_processor(Site.objects.get(pk=1))
        campaign_params = {
            "type": "MainCampaign",
            "template": "discount",
            "team": self.TEAM,
            "status": "active"
        }
        sub_campaign_params = {
            "type": "SubCampaign",
            "template": "sub_redemption",
            "voucher_type": "generic",
            "triggers_on": "redemption",
            "status": "active"
        }
        reward_params = {
            "type": "SetDiscount",
            "discount_type": "percentage",
            "discount_value": 15
        }

        processor.create_campaign(campaign_name, **campaign_params)
        campaign_id = processor.response_content['id']
        processor.clear_response_variables()
        sub_campaign_params["parent_id"] = campaign_id
        processor.create_campaign(sub_campaign_name, **sub_campaign_params)
        sub_campaign_id = processor.response_content['id']
        processor.clear_response_variables()
        processor.create_reward(sub_campaign_id, **reward_params)
        reward_id = processor.response_content['id']
        processor.clear_response_variables()
        processor.create_voucher(voucher_code, sub_campaign_id)
        processor.clear_response_variables()

        processor.get_vouchers(sub_campaign_id)
        self.assertTrue(processor.is_request_success)
        self.assertGreater(len(processor.response_content), 0)

        processor.delete_voucher(voucher_code)
        processor.delete_reward(reward_id)
        processor.delete_campaign(sub_campaign_id)
        processor.delete_campaign(campaign_id)

    def test_get_vouchers_fail(self):
        processor = self.promo_processor(Site.objects.get(pk=1))
        processor.get_vouchers(-2)
        self.assertFalse(processor.is_request_success)

    # def test_get_voucher_success(self):
    #     raise NotImplementedError

    # def test_get_voucher_fail(self):
    #     raise NotImplementedError

    # def test_update_voucher_success(self):
    #     raise NotImplementedError

    # def test_update_voucher_fail(self):
    #     raise NotImplementedError

    # def test_delete_voucher_success(self):
    #     raise NotImplementedError

    # def test_delete_voucher_fail(self):
    #     raise NotImplementedError

    #############
    # Redeem
    # def test_create_redeem_success(self):
    #     raise NotImplementedError

    # def test_create_redeem_fail(self):
    #     raise NotImplementedError

    # def test_get_redeem_success(self):
    #     raise NotImplementedError

    # def test_get_redeem_fail(self):
    #     raise NotImplementedError

    # def test_update_redeem_success(self):
    #     raise NotImplementedError

    # def test_update_redeem_fail(self):
    #     raise NotImplementedError

    # def test_delete_redeem_success(self):
    #     raise NotImplementedError

    # def test_delete_redeem_fail(self):
    #     raise NotImplementedError

    # def test_confirm_redeem_success(self):
    #     raise NotImplementedError

    # def test_confirm_redeem_fail(self):
    #     raise NotImplementedError

    ################
    # Promotion Management
    def create_promo_automate_success(self):
        promo_code = 'PROMO-TEST'
        promo_offer = Offer.objects.get(pk=1)
        promo_name = f"{promo_offer.name}-{promo_code}"
        promo_form = PromoForm({
            'name': promo_name,
            'code': promo_code,
            'offer': promo_offer})
        promo_form.is_bound = True
        processor = self.promo_processor(Site.objects.get(pk=1))

        processor.create_promo_automate(promo_form)
        self.assertTrue(processor.is_request_success)
        self.assertEquals(Promo.objects.all().last().code, promo_code)

        promo = Promo.objects.get(name=promo_name)
        processor.get_campaign(promo.campaign_id)
        campaign_detials = processor.response_content
        reward_id = campaign_detials['children'][0]['rewards'][0]['id']
        subcampaign_id = campaign_detials['children'][0]['id']

        processor.delete_voucher(promo.code)
        processor.delete_reward(reward_id)
        processor.delete_campaign(subcampaign_id)
        processor.delete_campaign(campaign_detials['id'])

    # def test_create_promo_success(self, promo_form):
    #     raise NotImplementedError

    # def test_create_promo_fail(self, promo_form):
    #     raise NotImplementedError

    # def test_update_promo_success(self, promo_form):
    #     raise NotImplementedError

    # def test_update_promo_fail(self, promo_form):
    #     raise NotImplementedError

    # def test_delete_promo_success(self, promo):
    #     raise NotImplementedError

    # def test_delete_promo_fail(self, promo):
    #     raise NotImplementedError

    ################
    # Processor Functions
    # def test_is_code_valid_success(self, code):
    #     raise NotImplementedError

    # def test_is_code_valid_fail(self, code):
    #     raise NotImplementedError

    # def test_redeem_code_success(self, code):
    #     raise NotImplementedError

    # def test_redeem_code_fail(self, code):
    #     raise NotImplementedError

    # def test_confirm_redeemed_code_success(self, code):
    #     raise NotImplementedError

    # def test_confirm_redeemed_code_fail(self, code):
    #     raise NotImplementedError

    # def test_process_promo_success(self, offer, promo_code):
    #     raise NotImplementedError

    # def test_process_promo_fail(self, offer, promo_code):
    #     raise NotImplementedError
