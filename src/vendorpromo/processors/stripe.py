import math
from vendor.config import DEFAULT_CURRENCY
from vendorpromo.processors.base import PromoProcessorBase
from vendor.processors.stripe import StripeProcessor as StripeBuilder


class StripePromoProcessor(PromoProcessorBase):
    stripe_builder = None

    def __init__(self, site, invoice=None):
        super().__init__(site, invoice)
        self.stripe_builder = StripeBuilder(self.site)

    # Stripe Object Builders
    ##########
    def build_coupon(self, promotional_campaign):
        coupon_data = {
            'name': promotional_campaign.name,
            'amount_off': self.stripe_builder.convert_decimal_to_integer(math.fabs(promotional_campaign.applies_to.current_price())) if not promotional_campaign.is_percent_off else None,
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

    def create_stripe_coupon(self, promotional_campaign):
        coupon_data = self.build_coupon(promotional_campaign)
        stripe_coupon = self.stripe_builder.stripe_create_object(self.stripe_builder.stripe.Coupon, coupon_data)

        if not stripe_coupon:
            return None  # Think about returning an error
        
        promotional_campaign.meta['stripe_id'] = stripe_coupon.id
        promotional_campaign.applies_to.meta['stripe_id'] = stripe_coupon.id
        promotional_campaign.save()

        return promotional_campaign

    def update_stripe_coupon(self, promotional_campaign):
        coupon_data = self.build_coupon(promotional_campaign)
        del(coupon_data['amount_off'])
        del(coupon_data['percent_off'])
        del(coupon_data['currency'])

        stripe_coupon = self.stripe_builder.stripe_update_object(self.stripe_builder.stripe.Coupon, promotional_campaign.meta['stripe_id'], coupon_data)

        if not stripe_coupon:
            return None  # Think about returning an error

    def create_stripe_promotion_code(self, coupon_code):
        promotion_code_data = self.build_promotion_code(coupon_code)
        stripe_promotion_code = self.stripe_builder.stripe_create_object(self.stripe_builder.stripe.PromotionCode, promotion_code_data)

        if not stripe_promotion_code:
            return None  # Think about returning an error
        
        coupon_code.meta['stripe_id'] = stripe_promotion_code.id
        coupon_code.save()

        return coupon_code

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
        
        return stripe_coupon

    def set_active_stripe_promotion_code(self, coupon_code, is_active):
        promotion_code_data = self.build_promotion_code(coupon_code)
        promotion_code_data['active'] = is_active
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
            self.stripe_builder.stripe_delete_object(self.stripe_builder.stripe.Coupon, stripe_id)
        
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

    def set_active_coupon_code(self, coupon_code, is_active):
        super().set_active_coupon_code(coupon_code, is_active)
        self.set_active_stripe_promotion_code(coupon_code, is_active)

        return coupon_code

    ################
    # Processor Functions
    def is_code_valid(self, coupon_code):
        if 'stripe_id' not in coupon_code.meta:
            return False
        
        return True
        
    def redeem_code(self, code):
        """
        Overwrite funtion to call external promo services to redeem code.
        Eg. call Vouchary.io API to redeem the code.
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
