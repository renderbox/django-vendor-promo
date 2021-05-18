import requests
import json

from django.utils.translation import ugettext_lazy as _

from vendorpromo.config import VENDOR_PROMO_PROCESSOR_URL, VENDOR_PROMO_PROCESSOR_BARRER_KEY
from vendorpromo.models import Promo
from vendorpromo.processors.base import PromoProcessorBase


class VoucheryProcessor(PromoProcessorBase):

    BASE_URL = VENDOR_PROMO_PROCESSOR_URL
    BARRER_KEY = VENDOR_PROMO_PROCESSOR_BARRER_KEY

    CAMPAIGN_URL = 'campaigns/'
    VOUCHER_URL = 'vouchers/'
    REDEMPTION_URL = 'redemptions/'

    ############################
    # Utils
    def process_response(self):
        self.response_content = json.loads(self.response.content)
        self.response_message = self.response_content.get('message')
        if "error" in self.response_content or self.response_content.get('type') == "Error":
            self.response_errors = self.response_content.get("errors")
            self.is_request_success = False
        else:
            self.is_request_success = True

    def get_headers(self):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.BARRER_KEY}"
        }

    def get_url(self, path_route):
        """
        Function returns the full url to make the api call to vouchery's
        endpoint. It recieves a list of headeres that will be appended
        to the BASE_URLS.
        params:
        path_route: List of string path_route
        returns:
        full_url: string with the appended path_route
        """
        path_route.insert(0, self.BASE_URL)
        return "/".join(path_route)

    ############################
    # VOUCHERY API CALLS
    #############
    # Campaigns
    def create_campaign(self, name, description=""):
        url = self.get_url([self.CAMPAIGN_URL])
        if not name:
            raise ValueError(_("name is required to create a campaign"))
        payload = {
            "type": "MainCampaign",
            "name": name,
            # TODO: Add ability to choose from [discount, loyalty, gift_card]
            "template": "discount",
            "description": description
        }

        self.response = requests.request("POST", url, json=payload, headers=self.get_headers())
        self.process_response()

    def get_campaign(self, id):
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
        if not self.process_response(response):
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
        if not self.process_response(response):
            return None
        promo.save()

    def delete_promo(self, promo):
        '''
        Override if you need to do additional steps when deleting a Promo instance,
        such as editing the promo code in an external service if needed.
        '''
        response = self.delete_voucher(promo)
        if not self.process_response(response):
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
        if self.process_response(response):
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
        self.process_response(response)

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
