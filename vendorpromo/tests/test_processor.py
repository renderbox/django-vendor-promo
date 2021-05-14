from django.test import TestCase


class BaseProcessorTests(TestCase):

    def setUp(self):
        pass

    def test_create_promo_success(self):
        raise NotImplementedError

    def test_create_promo_fail(self):
        raise NotImplementedError

    def test_update_promo_success(self):
        raise NotImplementedError

    def test_update_promo_fail(self):
        raise NotImplementedError

    def test_delete_promo_success(self):
        raise NotImplementedError

    def test_delete_promo_fail(self):
        raise NotImplementedError

    def test_is_code_valid_success(self):
        raise NotImplementedError

    def test_is_code_valid_fail(self):
        raise NotImplementedError

    def test_redeem_code_success(self):
        raise NotImplementedError

    def test_redeem_code_fail(self):
        raise NotImplementedError

    def test_confirm_redeemed_code_success(self):
        raise NotImplementedError

    def test_confirm_redeemed_code_fail(self):
        raise NotImplementedError

    def test_process_promo_success(self):
        raise NotImplementedError

    def test_process_promo_fail(self):
        raise NotImplementedError


class VoucherProcessorTests(TestCase):

    def setUp(self):
        pass

    # Utils
    def test_check_response_success(self, response):
        raise NotImplementedError

    def test_check_response_fail(self, response):
        raise NotImplementedError

    def test_get_headers_success(self):
        raise NotImplementedError

    def test_get_headers_fail(self):
        raise NotImplementedError

    ############################
    # VOUCHERY API CALLS

    #############
    # Campaigns
    def test_create_campaign_success(self, name, description):
        raise NotImplementedError

    def test_create_campaign_fail(self, name, description):
        raise NotImplementedError

    def test_get_campaign_success(self, id):
        raise NotImplementedError

    def test_get_campaign_fail(self, id):
        raise NotImplementedError

    def test_update_campaign_success(self):
        raise NotImplementedError

    def test_update_campaign_fail(self):
        raise NotImplementedError

    def test_delete_campaign_success(self):
        raise NotImplementedError

    def test_delete_campaign_fail(self):
        raise NotImplementedError

    #############
    # Redeem
    def test_create_redeem_success(self):
        raise NotImplementedError

    def test_create_redeem_fail(self):
        raise NotImplementedError

    def test_get_redeem_success(self):
        raise NotImplementedError

    def test_get_redeem_fail(self):
        raise NotImplementedError

    def test_update_redeem_success(self):
        raise NotImplementedError

    def test_update_redeem_fail(self):
        raise NotImplementedError

    def test_delete_redeem_success(self):
        raise NotImplementedError

    def test_delete_redeem_fail(self):
        raise NotImplementedError

    def test_confirm_redeem_success(self):
        raise NotImplementedError

    def test_confirm_redeem_fail(self):
        raise NotImplementedError

    #############
    # Voucher
    def test_create_voucher_success(self):
        raise NotImplementedError

    def test_create_voucher_fail(self):
        raise NotImplementedError

    def test_get_voucher_success(self):
        raise NotImplementedError

    def test_get_voucher_fail(self):
        raise NotImplementedError

    def test_update_voucher_success(self):
        raise NotImplementedError

    def test_update_voucher_fail(self):
        raise NotImplementedError

    def test_delete_voucher_success(self):
        raise NotImplementedError

    def test_delete_voucher_fail(self):
        raise NotImplementedError

    ################
    # Promotion Management
    def test_create_promo_success(self, promo_form):
        raise NotImplementedError

    def test_create_promo_fail(self, promo_form):
        raise NotImplementedError

    def test_update_promo_success(self, promo_form):
        raise NotImplementedError

    def test_update_promo_fail(self, promo_form):
        raise NotImplementedError

    def test_delete_promo_success(self, promo):
        raise NotImplementedError

    def test_delete_promo_fail(self, promo):
        raise NotImplementedError

    ################
    # Processor Functions
    def test_is_code_valid_success(self, code):
        raise NotImplementedError

    def test_is_code_valid_fail(self, code):
        raise NotImplementedError

    def test_redeem_code_success(self, code):
        raise NotImplementedError

    def test_redeem_code_fail(self, code):
        raise NotImplementedError

    def test_confirm_redeemed_code_success(self, code):
        raise NotImplementedError

    def test_confirm_redeemed_code_fail(self, code):
        raise NotImplementedError

    def test_process_promo_success(self, offer, promo_code):
        raise NotImplementedError

    def test_process_promo_fail(self, offer, promo_code):
        raise NotImplementedError
