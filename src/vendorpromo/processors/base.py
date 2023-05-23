import math

from django.utils import timezone
from vendor.models import Offer, Price


#############
# BASE CLASS
class PromoProcessorBase(object):
    site = None
    promo = None
    invoice = None
    redeemed = False

    response = None
    response_content = None
    response_error = None
    response_message = None
    is_request_success = False

    def __init__(self, site, invoice=None):
        self.site = site
        if invoice is not None:
            self.invoice = invoice

    ################
    # Utils
    def clear_response_variables(self):
        self.response = None
        self.response_content = None
        self.response_error = None
        self.response_message = None
        self.is_request_success = False

    def set_promo_invoice_vendor_notes(self, code):
        if self.invoice is None:
            # TODO: Should this raise an exception, probably.
            return None

        if not self.invoice.vendor_notes:
            self.invoice.vendor_notes = {}
            self.invoice.vendor_notes['promos'] = {}

        if 'promos' in self.invoice.vendor_notes.keys():
            if code not in self.invoice.vendor_notes['promos'].keys():
                self.invoice.vendor_notes['promos'][code] = False
        else:
            self.invoice.vendor_notes['promos'] = {code: False}

        self.invoice.save()

    def create_promo_offer(self, promo_campaign, products, cost):
        now = timezone.now()
        promo_offer = Offer()
        promo_offer.name = promo_campaign.name
        promo_offer.start_date = now
        promo_offer.site = promo_campaign.site
        promo_offer.is_promotional = True
        promo_offer.save()

        for product in products:
            promo_offer.products.add(product)

        price = Price()
        price.offer = promo_offer

        if not promo_campaign.is_percent_off:
            price.cost = -math.fabs(cost)
        else:
            price.cost = math.fabs(cost)

        price.start_date = now
        price.save()

        return promo_offer

    def update_promo_offer(self, promo_campaign, products, cost):
        promo_campaign.applies_to.name = promo_campaign.name
        promo_campaign.applies_to.products.clear()

        for product in products:
            promo_campaign.applies_to.products.add(product)
        promo_campaign.applies_to.save()

        update_price = promo_campaign.applies_to.prices.first()
        update_price.cost = cost
        update_price.save()

        promo_campaign.save()
    
    ################
    # Promotion Management
    def create_promo(self, promo_form):
        '''
        Override if you need to do additional steps when creating a Promo instance,
        such as creating the promo code in an external service if needed.
        '''
        promo_campaign = promo_form.save(commit=False)
        promo_campaign.site = self.site
        promo_campaign.applies_to = self.create_promo_offer(promo_campaign, promo_form.cleaned_data['applies_to'], promo_form.cleaned_data['discount_value'])
        promo_campaign.save()
        
        return promo_campaign
        
    def update_promo(self, promo_form):
        '''
        Override if you need to do additional steps when updating a Promo instance,
        such as editing the promo code in an external service if needed.
        '''
        promo_campaign = promo_form.save(commit=False)
        promo_campaign.site = self.site

        if promo_form.cleaned_data['is_percent_off'] is not None:
            promo_campaign.is_percent_off = promo_form.cleaned_data['is_percent_off']

        self.update_promo_offer(promo_campaign, promo_form.cleaned_data['applies_to'], promo_form.cleaned_data['discount_value'])

        promo_campaign.save()

        return promo_campaign

    def delete_promo(self, promo_campaign):
        '''
        Override if you need to do additional steps when deleting a Promo instance,
        such as editing the promo code in an external service if needed.
        '''
        promo_campaign.delete()

    ################
    # Coupon Code Management
    def create_coupon_code(self, coupon_form):
        coupon_code = coupon_form.save(commit=True)
        return coupon_code

    def update_coupon_code(self, coupon_form):
        coupon_code = coupon_form.save(commit=True)
        return coupon_code

    def delete_coupon_code(self, coupon_code):
        coupon_code.delete()

    ################
    # Processor Functions
    def is_code_valid(self, code):
        """
        Overwrite funtion to call external promo services.
        Eg. call Vouchary.io API to see if the code entered is valid.
        """
        raise NotImplementedError

    def redeem_code(self, code):
        """
        Overwrite funtion to call external promo services to redeem code.
        Eg. call Vouchary.io API to redeem the code.
        """
        raise NotImplementedError

    def confirm_redeemed_code(self, code):
        """
        Overwrite funtion to call external promo services to confirm
        that the redeem code was applied.
        Eg. call Vouchary.io API to confirm redeem the code was applied.
        """
        raise NotImplementedError

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
