import requests

from vendorpromo.config import VENDOR_PROMO_PROCESSOR_URL, VENDOR_PROMO_PROCESSOR_BARRER_KEY
from vendorpromo.models import Promo
from vendorpromo.processors import PromoProcessorBase


class VoucheryProcessor(PromoProcessorBase):

    BASE_URL = VENDOR_PROMO_PROCESSOR_URL
    BARRER_KEY = VENDOR_PROMO_PROCESSOR_BARRER_KEY

    CAMPAIGN_URL = 'campaigns/'
    VOUCHER_URL = 'vouchers/'
    REDEMPTION_URL = 'redemptions/'

    ############################
    # Utils
    def check_response(self, response):
        # if response ok return True
        # else self.response_error = error from response return False
        raise NotImplementedError

    ############################
    # VOUCHERY API CALLS

    #############
    # Campaigns
    def create_campaign(self):
        # Voucher Example
        # url = self.BASE_URL + self.CAMPAIGN_URL
        # payload = {"type": "MainCampaign"}
        # headers = {
        #     "Accept": "application/json",
        #     "Content-Type": "application/json"
        # }
        # response = requests.request("POST", url, json=payload, headers=headers)
        # print(response.text)
        raise NotImplementedError

    def get_campaign(self):
        raise NotImplementedError

    def update_campaign(self):
        raise NotImplementedError

    def delete_campaign(self):
        raise NotImplementedError

    #############
    # Redeem
    def create_redeem(self):
        raise NotImplementedError

    def get_redeem(self):
        raise NotImplementedError

    def update_redeem(self):
        raise NotImplementedError

    def delete_redeem(self):
        raise NotImplementedError

    def confirm_redeem(self):
        raise NotImplementedError

    #############
    # Voucher
    def create_voucher(self):
        raise NotImplementedError

    def get_voucher(self):
        raise NotImplementedError

    def update_voucher(self):
        raise NotImplementedError

    def delete_voucher(self):
        raise NotImplementedError

    ################
    # Promotion Management
    def create_promo(self, promo_form):
        '''
        Before saving the promo model instance form the form it calls
        Vouchery.io API to create it and checks if it was successful. If
        it was it will save the promo instance record. 
        '''
        promo = promo_form.save(commit=False)
        response = self.create_campaign(promo.campaign_name)
        if not self.check_response(response):
            return None
        promo.save()

    def update_promo(self, promo_form):
        '''
        Before updateing the promo record it calls Vouchery.io API to
        update the voucher on their end. If successful it saves the
        updated promo instance.
        '''
        promo = promo_form.save(commit=False)
        response = self.update_voucher(promo)
        if not self.check_response(response):
            return None
        promo.save()

    def delete_promo(self, promo):
        '''
        Override if you need to do additional steps when deleting a Promo instance,
        such as editing the promo code in an external service if needed.
        '''
        response = self.delete_voucher(promo)
        if not self.check_response(response):
            return None
        Promo.objects.delete(promo)

    ################
    # Processor Functions
    def is_code_valid(self, code):
        """
        Vouchery.io create_redeem validates the code. If it is valid
        it will create a redemption recode to be confirmed after payment.
        """
        response = self.create_redeem(code)
        if self.check_response(response):
            return True
        return False

    def redeem_code(self, code):
        """
        Function those not need to be implemented as the is_code_valid function
        checks if the code is valid and creates a redemption.
        """
        pass

    def confirm_redeemed_code(self, code):
        """
        After purchase with a promo code the funtion should be called to
        confirm that the promo code was used.
        """
        response = self.confirm_redeem(code)
        self.check_response(response)

    def process_promo(self, offer, promo_code):
        '''
        Function used to check if the promo code is valid through external
        promo services such as Vouchery.io. If the code is valid it will
        redeem it.
        NOTE: after purchase, one should confirm that the code
        was applied to an invoice.
        '''
        if not self.is_code_valid(promo_code):
            return None
        self.redeem_code(promo_code)
