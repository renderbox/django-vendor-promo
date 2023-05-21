from vendor.config import DEFAULT_CURRENCY
from vendorpromo.processors.base import PromoProcessorBase
from vendor.processors.stripe_processor import StripeProcessor as StripeBuilder


class StripePromoProcessor(PromoProcessorBase):
    site = None
    stripe_builder = None

    def __init__(self, site):
        self.site = site
        self.stripe_builder = StripeBuilder(self.site)

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
    # Stripe Object Builders
    ##########
    def build_coupon(self, promotional_campaign):
        coupon_data = {
            'name': promotional_campaign.name,
            'amount_off': promotional_campaign.applies_to.current_price() if not promotional_campaign.is_percent_off else None,
            'percent_off': promotional_campaign.applies_to.current_price() if promotional_campaign.is_percent_off else None,
            'metadata': {'site': promotional_campaign.site},
            'duration': promotional_campaign.meta.get('duration'),
            'duration_in_months': promotional_campaign.meta.get('duration_in_months'),
            'max_redemptions': promotional_campaign.max_redemptions,
            'redeem_by': promotional_campaign.end_date,
            'currency': DEFAULT_CURRENCY,  # TODO: Multicurrency support
            'applies_to': None  # Need to figure out how to implement since we are syncing offers not products with stripe
        }

        return coupon_data


    def create_stripe_coupon(self, promotional_campaign):
        coupon_data = self.build_coupon(promotional_campaign)
        stripe_coupon = self.stripe_builder.stripe_create_object(self.stripe_builder.stripe.Coupon, coupon_data)

        if not stripe_coupon:
            return None  # Think about returning an error
        
        promotional_campaign.meta['stripe_id'] = stripe_coupon.id
        promotional_campaign.applies_to.meta['stripe_id'] = stripe_coupon.id
        promotional_campaign.save()

    
    def update_stripe_coupon(self, promotional_campaign):
        coupon_data = self.build_coupon(promotional_campaign)
        del(coupon_data['amount_off'])
        del(coupon_data['percent_off'])
        del(coupon_data['currency'])
        stripe_coupon = self.stripe_builder.stripe_update_object(self.stripe_builder.stripe.Coupon, promotional_campaign.meta['stripe_id'], coupon_data)

        if not stripe_coupon:
            return None  # Think about returning an error

    
    ################
    # Promotion Management
    def create_promo(self, promo_form):
        '''
        Override if you need to do additional steps when creating a Promo instance,
        such as creating the promo code in an external service if needed.
        '''
        ...

    def update_promo(self, promo_form):
        '''
        Override if you need to do additional steps when updating a Promo instance,
        such as editing the promo code in an external service if needed.
        '''
        promo = promo_form.save(commit=False)
        promo.save()

    def delete_promo(self, promo_campaign):
        '''
        Override if you need to do additional steps when deleting a Promo instance,
        such as editing the promo code in an external service if needed.
        '''
        stripe_id = promo_campaign.meta.get('stripe_id')
        
        if stripe_id:
            self.stripe_builder.stripe_delete_object(self.stripe.Coupon, stripe_id)

        promo_campaign.delete()

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
