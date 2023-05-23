from vendor.config import DEFAULT_CURRENCY
from vendorpromo.processors.base import PromoProcessorBase
from vendor.processors.stripe_processor import StripeProcessor as StripeBuilder


class StripePromoProcessor(PromoProcessorBase):
    stripe_builder = None

    def __init__(self, site):
        super().__init__(site)
        self.stripe_builder = StripeBuilder(self.site)

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
    
    def build_promotion_code(self, coupon_code):
        promotion_code_data = {
            "coupon": coupon_code.promo.meta['stripe_id'],
            "code": coupon_code.code,
            'metadata': {'site': coupon_code.promo.site},
            "active": coupon_code.active,
            "expires_at": coupon_code.end_date,
            "max_redemptions": coupon_code.max_redemptions,
            "restrictions": None  # TODO: Implement option
        }

        return promotion_code_data

    def create_stripe_promotion_code(self, coupon_code):
        promotion_code_data = self.build_promotion_code(coupon_code)
        stripe_promotion_code = self.stripe_builder.stripe_create_object(self.stripe_builder.stripe.PromotionCode, promotion_code_data)

        if not stripe_promotion_code:
            return None  # Think about returning an error
        
        coupon_code.meta['stripe_id'] = stripe_promotion_code.id
        coupon_code.applies_to.meta['stripe_id'] = stripe_promotion_code.id
        coupon_code.save()

    def update_stripe_promotion_code(self, coupon_code):
        promotion_code_data = self.build_promotion_code(coupon_code)
        del(promotion_code_data['coupon'])
        del(promotion_code_data['code'])
        del(promotion_code_data['metadata'])
        del(promotion_code_data['expires_at'])
        del(promotion_code_data['max_redemptions'])

        stripe_coupon = self.stripe_builder.stripe_update_object(self.stripe_builder.stripe.PromotionCode, coupon_code.meta['stripe_id'], promotion_code_data)

        if not stripe_coupon:
            return None  # Think about returning an error

    ################
    # Promotion Management
    def create_promo(self, promo_form):
        '''
        Override if you need to do additional steps when creating a Promo instance,
        such as creating the promo code in an external service if needed.
        '''
        promo_campaign = super().create_promo(promo_form)
        self.create_stripe_coupon(promo_campaign)
        
        return promo_campaign

    def update_promo(self, promo_form):
        '''
        Override if you need to do additional steps when updating a Promo instance,
        such as editing the promo code in an external service if needed.
        '''
        promo_campaign = super().update_promo(promo_form)
        self.update_stripe_coupon(promo_campaign)

        return promo_campaign

    def delete_promo(self, promo_campaign):
        '''
        Override if you need to do additional steps when deleting a Promo instance,
        such as editing the promo code in an external service if needed.
        '''
        stripe_id = promo_campaign.meta.get('stripe_id')
        
        if stripe_id:
            self.stripe_builder.stripe_delete_object(self.stripe.Coupon, stripe_id)
        
        super().delete_promo(promo_campaign)

    ################
    # Coupon Code Management
    def create_coupon_code(self, coupon_form):
        coupon_code = super().create_coupon_code(coupon_form)
        self.create_stripe_promotion_code(coupon_code)

        return coupon_code

    def update_coupon_code(self, coupon_form):
        coupon_code = super().update_coupon_code(coupon_form)
        self.update_stripe_promotion_code(coupon_code)

        return coupon_code

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
