import uuid

from autoslug import AutoSlugField

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from django.utils.translation import ugettext_lazy as _

from vendor.models import Offer
from vendor.models.base import CreateUpdateModelBase
from vendor.utils import set_default_site_id


class Promo(CreateUpdateModelBase):
    '''
    This is the base class that all Promo should inherit from.
    '''
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(_("Promo Name"), max_length=80, blank=False)
    description = models.TextField(_("Promo Description"), default=None, blank=True, null=True, help_text=_("Enter a description for your Promo Code"))
    code = models.CharField(_("Code"), max_length=80, blank=False)
    campaign_id = models.CharField(_("Campaign Identifier"), max_length=80, blank=True, null=True)
    campaign_name = models.CharField(_("Campaign Name"), max_length=100, blank=True, null=True)
    campaign_description = models.TextField(_("Campaign Description"), blank=True, null=True)
    meta = models.JSONField(_("Meta"), default=dict)
    slug = AutoSlugField(populate_from='name', unique_with='site__id')
    site = models.ForeignKey(Site, verbose_name=_("Site"), on_delete=models.CASCADE, default=set_default_site_id, related_name="promos")
    offer = models.ForeignKey(Offer, blank=False, null=False, related_name="offer")

    objects = models.Manager()
    on_site = CurrentSiteManager()

    class Meta:
        verbose_name = "Promo"
        verbose_name_plural = "Promos"

