import requests
import json

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

from vendorpromo.config import VENDOR_PROMO_PROCESSOR_URL, VENDOR_PROMO_PROCESSOR_BARRER_KEY
from vendorpromo.integrations import VoucheryIntegration
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
    BASE_URL = None
    BARRER_KEY = None
    CAMPAIGN_URL = 'campaigns'
    REWARDS_URL = 'rewards'
    VOUCHER_URL = 'vouchers'
    REDEMPTION_URL = 'redemptions'

    CAMPAIGN_PARAMS = {
        "type": "MainCampaign",
        "template": "discount",
        "status": "active"
    }
    SUBCAMPAIGN_PARAMS = {
        "type": "SubCampaign",
        "template": "sub_redemption",
        "voucher_type": "generic",
        "triggers_on": "redemption",
        "status": "active"
    }
    REWARD_PARAMS = {
        "type": "SetDiscount",
        "discount_type": "percentage",
        "discount_value": 0  # The actual discount is set in the Offer instance.
    }
    credentials = None

    def __init__(self, site, invoice=None):
        super().__init__(invoice=invoice)
        self.set_credentials(site)


    def set_credentials(self, site):
        self.credentials = VoucheryIntegration(site)
        if self.credentials.instance:
           self.BASE_URL = self.credentials.instance.client_url
           self.BARRER_KEY = self.credentials.instance.private_key
        elif VENDOR_PROMO_PROCESSOR_URL and VENDOR_PROMO_PROCESSOR_BARRER_KEY:
           self.BASE_URL = VENDOR_PROMO_PROCESSOR_URL
           self.BARRER_KEY = VENDOR_PROMO_PROCESSOR_BARRER_KEY
        else:
            raise ImproperlyConfigured("Vouchery is not properly Configured. Missing BASE_URL and/or BARRER_KEY")


    ################
    # Promotion Management
    def create_promo_automate(self, promo_form):
        '''
        This function automates the steps required to create a voucher/promo-code
        in Vouchery. This means that it will create a campaign named affter the
        offer's product name, a sub-campaign named after the offer's a percentage reward
        and finally the voucher.
        After creation, a user can login to Vouchery and change the campaigns, and
        sub-campaigns name if desired. They should not change the promo code as it
        needs to be sent from vendor-promo
        '''
        promo = promo_form.save(commit=False)
        promo.campaign_name = promo.offer.site.name

        self.get_campaigns(**{'name_cont': promo.campaign_name})
        self.process_response()

        if not self.is_request_success:
            raise Exception(f"Create Promo Automate Failed: errors: {self.response_error}")
        
        self.is_request_success = False # Reset response flag

        # Checks if the Main Campaign already exists
        if not self.response_content:
            self.create_campaign(promo.campaign_name, **self.CAMPAIGN_PARAMS)
            if not self.is_request_success:
                raise Exception(_("Create Campaing Failed"))
            promo.campaign_id = str(self.response_content['id'])
        else:
            promo.campaign_id = str(self.response_content[0]['id'])

        self.clear_response_variables()
        self.get_sub_campaigns(**{'name_cont': promo.offer.name})

        # Checks if a SubCampaign already exists.
        if not self.response_content:
            self.SUBCAMPAIGN_PARAMS['parent_id'] = promo.campaign_id
            self.clear_response_variables()
            self.create_campaign(promo.offer.name, **self.SUBCAMPAIGN_PARAMS)
            del(self.SUBCAMPAIGN_PARAMS['parent_id'])
            if not self.is_request_success:
                raise Exception(_("Create Sub-Campaing Failed"))
            subcampaign_id = str(self.response_content['id'])
            parent_id = str(self.response_content['parent_id'])
        else:
            parent_id = str(self.response_content[0]['parent_id'])
            subcampaign_id = str(self.response_content[0]['id'])

        # Check that the SubCampaign is has the correct MainCampaing (Parent Campaign)
        if parent_id != promo.campaign_id:
            self.update_campaign(self.response_content[0]['id'], **{'parent_id': promo.campaign_id})

        self.get_campaign(subcampaign_id)
        if not self.response_content.get('rewards'):
            self.clear_response_variables()
            self.create_reward(subcampaign_id, **self.REWARD_PARAMS)
            if not self.is_request_success:
                raise Exception(_("Create Reward Failed"))

        self.clear_response_variables()
        self.create_voucher(promo.code, subcampaign_id)

        if not self.is_request_success:
            raise Exception(_("Create Voucher Failed"))

        promo.save()

    def create_promo(self, promo_form):
        '''
        Before saving the promo model instance form the form it calls
        Vouchery.io API to create it and checks if it was successful. If
        it was it will save the promo instance record.
        '''
        promo = promo_form.save(commit=False)
        self.create_voucher(promo.code, promo.campaign_id)
        if not self.is_request_success:
            return None
        promo.save()

    def update_promo(self, promo_form):
        '''
        Before updateing the promo record it calls Vouchery.io API to
        update the voucher on their end. If successful it saves the
        updated promo instance.
        '''
        promo = promo_form.save(commit=False)
        if 'code' in promo_form.changed_data:
            return None
        self.update_voucher(promo.code)
        if not self.is_request_success:
            return None
        promo.save()

    def delete_promo(self, promo):
        '''
        Override if you need to do additional steps when deleting a Promo instance,
        such as editing the promo code in an external service if needed.
        '''
        self.delete_voucher(promo.code)
        if not self.is_request_success and (self.response.status_code != 404 or self.response.status_code < 300):
            return None
        promo.delete()

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
                    self.response_error = self.response_content.get("error")
                else:
                    self.response_error = self.response_content.get("errors")
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

    def assemble_url(self, path_route):
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
        url = self.assemble_url([self.CAMPAIGN_URL])

        if not name:
            raise ValueError(_("name is required to create a campaign"))
        
        base_payload = {
            "name": name,
        }
        payload = {**base_payload, **optional_params}

        self.response = requests.request("POST", url, json=payload, headers=self.get_headers())
        self.process_response()

    def get_campaigns(self, **querystring):
        url = self.assemble_url([self.CAMPAIGN_URL])

        if not querystring:
            querystring = None

        self.response = requests.request("GET", url, headers=self.get_headers(), params=querystring)
        self.process_response()

    def get_sub_campaigns(self, **querystring):
        url = self.assemble_url([self.CAMPAIGN_URL, 'sub'])

        if not querystring:
            querystring = None

        self.response = requests.request("GET", url, headers=self.get_headers(), params=querystring)
        self.process_response()

    def get_campaign(self, campaign_id):
        url = self.assemble_url([self.CAMPAIGN_URL, str(campaign_id)])

        self.response = requests.request("GET", url, headers=self.get_headers())
        self.process_response()

    def update_campaign(self, campaign_id, **optional_params):
        url = self.assemble_url([self.CAMPAIGN_URL, str(campaign_id)])

        self.response = requests.request("PATCH", url, json=optional_params, headers=self.get_headers())
        self.process_response()

    def delete_campaign(self, campaign_id):
        url = self.assemble_url([self.CAMPAIGN_URL, str(campaign_id)])

        if not campaign_id:
            raise ValueError(_("campaign_id is required to delete a campaign"))

        self.response = requests.request("DELETE", url, headers=self.get_headers())
        self.process_response()

    def delete_full_campaign(self, campaign_id):
        self.get_campaign(campaign_id)

        sub_campaigns = [sub_campaign for sub_campaign in self.response_content['children'] if sub_campaign['type'] == 'SubCampaign']
        for sub_campaign in sub_campaigns:
            self.clear_response_variables()
            self.get_campaign(sub_campaign['id'])
            rewards = self.response_content['rewards']
            self.clear_response_variables()
            self.get_vouchers(sub_campaign['id'])
            if self.response_content:
                for voucher in self.response_content:
                    self.clear_response_variables()
                    self.delete_voucher(voucher['code'])
            for reward in rewards:
                self.clear_response_variables()
                self.delete_reward(reward['id'])
            self.delete_campaign(sub_campaign['id'])

        self.clear_response_variables()
        self.delete_campaign(campaign_id)

    #############
    # Reward
    def create_reward(self, campaign_id, **reward_params):
        url = self.assemble_url([self.CAMPAIGN_URL, str(campaign_id), self.REWARDS_URL])

        self.response = requests.request("POST", url, json=reward_params, headers=self.get_headers())
        self.process_response()

    def get_reward(self, reward_id):
        url = self.assemble_url([self.REWARDS_URL, str(reward_id)])

        self.response = requests.request('GET', url, headers=self.get_headers())
        self.process_response()

    def update_reward(self):
        raise NotImplementedError

    def delete_reward(self, reward_id):
        url = self.assemble_url([self.REWARDS_URL, str(reward_id)])

        self.response = requests.request("DELETE", url, headers=self.get_headers())
        self.process_response()

    #############
    # Voucher
    def create_voucher(self, code, campaign_id):
        url = self.assemble_url([self.CAMPAIGN_URL, str(campaign_id), self.VOUCHER_URL])

        payload = {
            "type": "Voucher",
            "active": True,
            "code": code,
            "status": "active"
        }

        self.response = requests.request("POST", url, json=payload, headers=self.get_headers())
        self.process_response()

    def get_vouchers(self, campaign_id, **kwargs):
        url = self.assemble_url([self.CAMPAIGN_URL, str(campaign_id), self.VOUCHER_URL])

        self.response = requests.request("GET", url, headers=self.get_headers())
        self.process_response()

    def get_voucher(self, code, **querystring):
        url = self.assemble_url([self.VOUCHER_URL, str(code)])

        if not querystring:
            querystring = None

        self.response = requests.request("GET", url, headers=self.get_headers(), params=querystring)
        self.process_response()

    def update_voucher(self):
        '''
        In vouchery you cannot update a voucher.
        '''
        pass

    def delete_voucher(self, code):
        url = self.assemble_url([self.VOUCHER_URL, code])

        self.response = requests.request("DELETE", url, headers=self.get_headers())
        self.process_response()

    #############
    # Redeem
    def create_redeem(self, voucher_code, transaction_id, total_cost):
        url = self.assemble_url([self.VOUCHER_URL, str(voucher_code), self.REDEMPTION_URL])

        payload = {
            "transaction_id": transaction_id,
            "total_transaction_cost": total_cost
        }

        self.response = requests.request("POST", url, json=payload, headers=self.get_headers())
        self.process_response()

    def get_redeems(self, campaign_id):
        url = self.assemble_url([self.CAMPAIGN_URL, str(campaign_id), self.REDEMPTION_URL])

        self.response = requests.request("GET", url, headers=self.get_headers())
        self.process_response()

    def get_redeem(self, voucher_code, transaction_id):
        url = self.assemble_url([self.VOUCHER_URL, str(voucher_code), self.REDEMPTION_URL])

        querystring = {
            "transaction_id": transaction_id
        }

        self.response = requests.request("GET", url, params=querystring, headers=self.get_headers())
        self.process_response()

    def delete_redeem(self, voucher_code, transaction_id):
        url = self.assemble_url([self.VOUCHER_URL, str(voucher_code), self.REDEMPTION_URL])

        querystring = {
            "transaction_id": transaction_id
        }

        self.response = requests.request("DELETE", url, params=querystring, headers=self.get_headers())
        self.process_response()

    def confirm_redeem(self, voucher_code, transaction_id):
        url = self.assemble_url([self.VOUCHER_URL, str(voucher_code), self.REDEMPTION_URL])

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
        self.create_redeem(code)
        if self.is_request_success:
            return True
        return False

    def is_code_valid_on_checkout(self, code, offer_cost):
        """
        Vouchery.io create_redeem validates the code. If it is valid
        it will create a redemption recode to be confirmed after payment.
        """
        # Checks to see if there is already a redemption that has not been confirmed.
        transaction_id = str(self.invoice.uuid) + f"__{code}"
        self.get_redeem(code, transaction_id)
        if self.is_request_success:
            self.set_promo_invoice_vendor_notes(code)
            return True
        self.create_redeem(code, transaction_id, offer_cost)
        if self.is_request_success:
            self.set_promo_invoice_vendor_notes(code)
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

    def process_promo(self, promo_code):
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
