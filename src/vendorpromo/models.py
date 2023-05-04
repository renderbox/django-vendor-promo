import uuid

from autoslug import AutoSlugField

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from vendor.models import CustomerProfile, Offer


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
class Promo(CreateUpdateModelBase):
    '''
    This is the base class that all Promo should inherit from.
    '''
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    description = models.TextField(_("Promo Description"), default=None, blank=True, null=True, help_text=_("Enter a description for your Promo Code"))
    code = models.CharField(_("Code"), max_length=80, blank=False)
    campaign_id = models.CharField(_("Campaign Identifier"), max_length=80, blank=True, null=True)
    campaign_name = models.CharField(_("Campaign Name"), max_length=100, blank=True, null=True)
    campaign_description = models.TextField(_("Campaign Description"), blank=True, null=True)
    meta = models.JSONField(_("Meta"), default=dict, blank=True, null=True)
    offer = models.ForeignKey(Offer, blank=False, null=False, related_name="promo", on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from='code', unique_with='offer__site__id')

    objects = models.Manager()

    class Meta:
        verbose_name = "Promo"
        verbose_name_plural = "Promos"

    def clean(self):
        if Promo.objects.filter(code=self.code, offer__site=self.offer.site).exists():
            raise ValidationError(_("Code already exists"))

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Affiliate(CreateUpdateModelBase):
    '''
    Class to link Customer Profiles or a general contact to a Promo
    '''
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    slug = AutoSlugField(unique_with='customer_profile__user__username')
    customer_profile = models.ForeignKey(CustomerProfile, blank=True, null=True, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=120, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    company = models.CharField(max_length=120, blank=True, null=True)
    promo = models.ManyToManyField(Promo, blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = "Affiliate"
        verbose_name_plural = "Affiliates"

    def __str__(self):
        if self.customer_profile:
            return str(self.customer_profile)
        
        if self.full_name:
            return self.full_name
        
        if self.email:
            return self.email
        
        if self.company:
            return self.company
        
        return self.uuid
