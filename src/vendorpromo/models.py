import uuid
import math

from autoslug import AutoSlugField
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from vendor.models import CustomerProfile, Invoice, Offer
from vendor.models.choice import InvoiceStatus

#######################################
# ABSTRACT MODELS
class CreateUpdateModelBase(models.Model):
    '''
    This is a shared models base that provides created & updated timestamp fields
    '''
    created = models.DateTimeField("date created", auto_now_add=True)
    updated = models.DateTimeField("last updated", auto_now=True)

    class Meta:
        abstract = True


#######################################
# MODELS

# To be deprecated
class Promo(CreateUpdateModelBase):
    '''
    This is the base class that all Promo should inherit from.
    '''
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    description = models.TextField(_("Promo Description"), default=None, blank=True, null=True, help_text=_("Enter a description for your Promo Code"))
    code = models.CharField(_("Code"), max_length=80, blank=False)  # This field will be depracted in favor of having the PromoCode Model
    campaign_id = models.CharField(_("Campaign Identifier"), max_length=80, blank=True, null=True)
    campaign_name = models.CharField(_("Campaign Name"), max_length=100, blank=True, null=True)
    campaign_description = models.TextField(_("Campaign Description"), blank=True, null=True)
    meta = models.JSONField(_("Meta"), default=dict, blank=True, null=True)
    offer = models.ForeignKey(Offer, blank=False, null=False, related_name="promo", on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from='code', unique_with='offer__site__id')

    objects = models.Manager()

    def __str__(self):
        return self.campaign_name
    
    class Meta:
        verbose_name = "Promo"
        verbose_name_plural = "Promos"

    def clean(self):
        if Promo.objects.filter(code=self.code, offer__site=self.offer.site).exists():
            raise ValidationError(_("Code already exists"))

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class PromotionalCampaign(CreateUpdateModelBase):
    '''
    Promotional Campaign is defined by it's name and description as intended to link between CouponCodes and Affiliates.
    A Promotional Campaign can only have one Affiliate, and can have multiple CouponCodes.
    The applies_to field is a connection to an vendor.offer that can be linked to multiple product models.
    The offer's price represents the discount to apply to the invoice and is controlled by the is_percent_off. 
    If is_percent_off is marked as true the offer.price is treated as a percentage.
    '''
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    campaign_id = models.CharField(_("Campaign Identifier"), max_length=80, blank=True, null=True)
    name = models.CharField(_("Campaign Name"), max_length=100, blank=True, null=True)
    description = models.TextField(_("Description"), default=None, blank=True, null=True, help_text=_("Enter a description or objective for this campaign"))
    start_date = models.DateTimeField(_("Start Date"), blank=True, null=True, help_text=_("The date when this promotion is valid from"))
    end_date = models.DateTimeField(_("End Date"), blank=True, null=True, help_text=_("The date when this promotion is no longer valid"))
    is_percent_off = models.BooleanField(_("Percent Off?"), default=False, help_text=_("Fixed Amount or Percent Off"))
    max_redemptions = models.IntegerField(_("Max Redemptions"), blank=True, null=True, help_text=_("The maximum redemptions for the whole promotion"))
    applies_to = models.ForeignKey(Offer, related_name=("promo_campaign"), blank=False, null=False, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, related_name=("promo_campaign"), on_delete=models.CASCADE, blank=False, null=False, verbose_name=_("Site"))
    meta = models.JSONField(_("Meta"), default=dict, blank=True, null=True)

    objects = models.Manager()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Promotional Campaign"
        verbose_name_plural = "Promotional Campaigns"
    

class CouponCode(CreateUpdateModelBase):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    active = models.BooleanField(_("Active"), default=True)
    code = AutoSlugField(unique_with=('promo__site'), editable=True, blank=True, null=True, sep="copy", verbose_name=_("Affiliate Code"))
    max_redemptions = models.IntegerField(_("Max Redemptions"), blank=True, null=True)
    end_date = models.DateTimeField(_("End Date"), blank=True, null=True, help_text=_("When will the code be unavailable"))
    meta = models.JSONField(blank=True, null=True, default=dict)
    promo = models.ForeignKey(PromotionalCampaign, related_name=("coupon_code"), blank=False, null=False, on_delete=models.CASCADE)
    invoice = models.ManyToManyField(Invoice, related_name=("coupon_code"), blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = "Coupon Code"
        verbose_name_plural = "Coupon Codes"

    def __str__(self):
        return self.code

    def get_display_code(self):
        return str(self.code).upper()
    
    def redemptions(self):
        return self.invoice.filter(status=InvoiceStatus.COMPLETE)

    def does_offer_apply(self, offer):
        if self.promo.applies_to.products.filter(pk__in=offer.products.all().values_list('pk', flat=True)):
            return True

        return False

    def get_discounted_amount(self, offer):
        """returns the discounted amount releated to the offer.

        Checks if the offer is related to the coupon_code. If it is,
        it returns the discounted amount from the the offer current_price.

        eg
        a):
            offer.current_price() = 80
            coupon_code.is_percent_off = True
            coupon_discount = 5%
            return (80 * 5) / 100
        b):
            offer.current_price() = 80
            coupon_code.is_percent_off = False
            coupon_discount = $5.00
            return 5.00

        Args:
            offer (Offer): Offer Model in django-vendo

        Returns:
            Decimal: The amount discounted
        """
        coupon_discount = 0

        if self.does_offer_apply(offer):
            coupon_discount = math.fabs(self.promo.applies_to.current_price())

            if self.promo.is_percent_off:
                return (offer.current_price() * coupon_discount) / 100
            else:
                return coupon_discount

        return 0


class Affiliate(CreateUpdateModelBase):
    '''
    Class to link Customer Profiles or a general contact to a Promo
    '''
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    slug = AutoSlugField(unique_with=('customer_profile__site'), editable=True, blank=True, null=True, verbose_name=_("Affiliate Code"))
    name = models.CharField(max_length=120, blank=True, null=True, verbose_name=_("Name"))
    type = models.CharField(max_length=80, blank=True, null=True, verbose_name=_("Type"))
    contact_name = models.CharField(max_length=120, blank=True, null=True, verbose_name=_("Contact Name"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email"))
    company = models.CharField(max_length=120, blank=True, null=True, verbose_name=_("Company"))
    customer_profile = models.ForeignKey(CustomerProfile, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("Customer Profile"))
    promo = models.ManyToManyField(PromotionalCampaign, blank=True, verbose_name=_("Promotion Campaign"))
    site = models.ForeignKey(Site, on_delete=models.CASCADE, blank=False, null=False, verbose_name=_("Site"))

    objects = models.Manager()

    class Meta:
        verbose_name = "Affiliate"
        verbose_name_plural = "Affiliates"

    def clean(self):
        if (self.customer_profile is None) and (self.contact_name is None and self.email is None and self.company is None and self.name is None):
            raise ValidationError(_("You at least need to assign a Customer Profile or enter a Name, Full Name, Email or Company for the Affiliate"))
        
        if self.customer_profile is not None and Affiliate.objects.filter(customer_profile=self.customer_profile).exists():
            raise ValidationError(_("The selected Customer Profile is already linked to an existing Affiliate."))

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        if self.customer_profile:
            return str(self.customer_profile)
        
        if self.name:
            return self.name
        
        if self.contact_name:
            return self.contact_name
        
        if self.email:
            return self.email
        
        if self.company:
            return self.company
        
        return self.uuid
