# App Settings
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

from siteconfigs.config import SiteConfigBaseClass
from siteconfigs.models import SiteConfigModel
from vendorpromo.forms import PromoProcessorForm, PromoProcessorSiteSelectForm, SupportedPromoProcessor


class PromoProcessorSiteConfig(SiteConfigBaseClass):
    label = _("Promo Code Processor")
    default = {"promo_processor": "base.PromoProcessorBase"}
    form_class = PromoProcessorForm

    def __init__(self, site=None):
        if site is None:
            site = Site.objects.get_current()
        self.key = ".".join([__name__, __class__.__name__])
        super().__init__(site, self.key)

    def get_form(self):
        return self.form_class(initial=self.get_initials())

    def get_initials(self):
        if self.instance:
            return {"promo_processor": [choice for choice in SupportedPromoProcessor.choices if choice[0] == self.instance.value["promo_processor"]][0]}
        return {"promo_processor": SupportedPromoProcessor.choices[0]}

    def get_selected_processor(self):
        if self.instance:
            return [choice for choice in SupportedPromoProcessor.choices if choice[0] == self.instance.value["promo_processor"]][0]
        return SupportedPromoProcessor.choices[0]  # Return Default Processors


class PromoProcessorSiteSelectSiteConfig(PromoProcessorSiteConfig):
    label = _("Promo Code Processor")
    default = {"promo_processor": "base.PromoProcessorBase"}
    form_class = PromoProcessorSiteSelectForm

    def get_initials(self):
        initial = super().get_initials()
        initial['site'] = (self.site.pk, self.site.domain)
        return initial

# Set up as a backup if the developer only want to set the processor through an enviornment variable
VENDOR_PROMO_PROCESSOR = getattr(settings, "VENDOR_PROMO_PROCESSOR", "dummy.DummyProcessor")

VENDOR_PROMO_PROCESSOR_URL = getattr(settings, "VENDOR_PROMO_PROCESSOR_URL")

VENDOR_PROMO_PROCESSOR_BARRER_KEY = getattr(settings, "VENDOR_PROMO_PROCESSOR_BARRER_KEY")
