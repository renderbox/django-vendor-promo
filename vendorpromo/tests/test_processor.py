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
