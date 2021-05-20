import requests
import json

from django.utils.translation import ugettext_lazy as _

from vendorpromo.config import VENDOR_PROMO_PROCESSOR_URL, VENDOR_PROMO_PROCESSOR_BARRER_KEY
from vendorpromo.models import Promo
from vendorpromo.processors.base import PromoProcessorBase


class VoucheryProcessor(PromoProcessorBase):
    """
    Vouchery Processor integrates Vouchery.io API to manage promotion codes.
    For more information on the available options you can look at: https://docs.vouchery.io/
    In Vouchery.io to have a Promo code you need to comply with the following structure:
    MainCampaign: [
        Sub-Campaign-A: {
            Reward: {
                    discount_type: [percentage, numeric, gift_card]
            }
            Vouchers: [
                {
                    code: string
                },
            ]
        },
    ]
    """

    BASE_URL = VENDOR_PROMO_PROCESSOR_URL
    BARRER_KEY = VENDOR_PROMO_PROCESSOR_BARRER_KEY

    CAMPAIGN_URL = 'campaigns'
    REWARDS_URL = 'rewards'
    VOUCHER_URL = 'vouchers'
    REDEMPTION_URL = 'redemptions'

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

    ############################
    # Utils
    def process_response(self):
        # TODO: God aweful code that needs to be cleaned up.
        if (b'[]' == self.response.content or b'' == self.response.content) and (self.response.status_code >= 200 and self.response.status_code < 300):
            self.is_request_success = True
            return None
        self.response_content = json.loads(self.response.content)
        if not isinstance(self.response_content, list):
            self.response_message = self.response_content.get('message')
            if self.response_content.get('type') == "Error":
                if "error" in self.response_content:
                    self.response_errors = self.response_content.get("error")
                else:
                    self.response_errors = self.response_content.get("errors")
                self.is_request_success = False
            else:
                self.is_request_success = True
        else:
            if self.response.status_code == 200:
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
    def create_campaign(self, name, **optional_params):
        url = self.get_url([self.CAMPAIGN_URL])

        if not name:
            raise ValueError(_("name is required to create a campaign"))
        base_payload = {
            "name": name,
        }
        payload = {**base_payload, **optional_params}

        self.response = requests.request("POST", url, json=payload, headers=self.get_headers())
        self.process_response()

    def get_campaigns(self, **querystring):
        url = self.get_url([self.CAMPAIGN_URL])

        if not querystring:
            querystring = None

        self.response = requests.request("GET", url, headers=self.get_headers(), params=querystring)
        self.process_response()

    def get_campaign(self, campaign_id):
        url = self.get_url([self.CAMPAIGN_URL, str(campaign_id)])

        self.response = requests.request("GET", url, headers=self.get_headers())
        self.process_response()

    def update_campaign(self, campaign_id, name, **optional_params):
        url = self.get_url([self.CAMPAIGN_URL, str(campaign_id)])

        # TODO: Need to remove hard coded type and template
        base_payload = {
            "type": "MainCampaign",
            "name": name,
            "template": "discount"
        }

        payload = {**base_payload, **optional_params}
        self.response = requests.request("PATCH", url, json=payload, headers=self.get_headers())
        self.process_response()

    def delete_campaign(self, campaign_id):
        url = self.get_url([self.CAMPAIGN_URL, str(campaign_id)])

        if not campaign_id:
            raise ValueError(_("campaign_id is required to delete a campaign"))

        self.response = requests.request("DELETE", url, headers=self.get_headers())
        self.process_response()

    #############
    # Reward
    def create_reward(self, campaign_id, **reward_params):
        url = self.get_url([self.CAMPAIGN_URL, str(campaign_id), self.REWARDS_URL])

        self.response = requests.request("POST", url, json=reward_params, headers=self.get_headers())
        self.process_response()

    def get_reward(self, reward_id):
        url = self.get_url([self.REWARDS_URL, str(reward_id)])

        self.response = requests.request('GET', url, headers=self.get_headers())
        self.process_response()

    def update_reward(self):
        raise NotImplementedError

    def delete_reward(self, reward_id):
        url = self.get_url([self.REWARDS_URL, str(reward_id)])

        self.response = requests.request("DELETE", url, headers=self.get_headers())
        self.process_response()

    #############
    # Voucher
    def create_voucher(self, code, campaign_id):
        url = self.get_url([self.CAMPAIGN_URL, str(campaign_id), self.VOUCHER_URL])

        payload = {
            "type": "Voucher",
            "active": True,
            "code": code,
            "status": "active"
        }

        self.response = requests.request("POST", url, json=payload, headers=self.get_headers())
        self.process_response()

    def get_vouchers(self, campaign_id, **kwargs):
        url = self.get_url([self.CAMPAIGN_URL, str(campaign_id), self.VOUCHER_URL])

        self.response = requests.request("GET", url, headers=self.get_headers())
        self.process_response()

    def get_voucher(self, code, **querystring):
        url = self.get_url([self.VOUCHER_URL, str(code)])

        if not querystring:
            querystring = None

        self.response = requests.request("GET", url, headers=self.get_headers(), params=querystring)
        self.process_response()

    def update_voucher(self):
        raise NotImplementedError

    def delete_voucher(self, code):
        url = self.get_url([self.VOUCHER_URL, code])

        self.response = requests.request("DELETE", url, headers=self.get_headers())
        self.process_response()

    #############
    # Redeem
    def create_redeem(self, voucher_code, transaction_id, total_cost):
        url = self.get_url([self.VOUCHER_URL, str(voucher_code), self.REDEMPTION_URL])

        payload = {
            "transaction_id": transaction_id,
            "total_transaction_cost": total_cost
        }

        self.response = requests.request("POST", url, json=payload, headers=self.get_headers())
        self.process_response()

    def get_redeems(self, campaign_id):
        url = self.get_url([self.CAMPAIGN_URL, str(campaign_id), self.REDEMPTION_URL])

        self.response = requests.request("GET", url, headers=self.get_headers())
        self.process_response()

    def get_redeem(self, voucher_code, transaction_id):
        url = self.get_url([self.VOUCHER_URL, str(voucher_code), self.REDEMPTION_URL])

        querystring = {
            "transaction_id": transaction_id
        }

        self.response = requests.request("GET", url, params=querystring, headers=self.get_headers())
        self.process_response()

    def delete_redeem(self, voucher_code, transaction_id):
        url = self.get_url([self.VOUCHER_URL, str(voucher_code), self.REDEMPTION_URL])

        querystring = {
            "transaction_id": transaction_id
        }

        self.response = requests.request("DELETE", url, params=querystring, headers=self.get_headers())
        self.process_response()

    def confirm_redeem(self, voucher_code, transaction_id):
        url = self.get_url([self.VOUCHER_URL, str(voucher_code), self.REDEMPTION_URL])

        querystring = {
            "transaction_id": transaction_id
        }

        self.response = requests.request("PATCH", url, params=querystring, headers=self.get_headers())
        self.process_response()

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
