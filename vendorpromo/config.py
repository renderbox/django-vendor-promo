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
    key = ""
    instance = None

    def __init__(self, site=None):
        if site is None:
            site = Site.objects.get_current()
        self.key = ".".join([__name__, __class__.__name__])
        self.set_instance(site)
        super().__init__(site, self.key)

    # TODO: This should be implemented in the SiteConfigBaseClass  
    def save(self, valid_form):
        site_config, created = SiteConfigModel.objects.get_or_create(site=self.site, key=self.key)
        site_config.value = {"promo_processor": valid_form.cleaned_data["promo_processor"]}
        site_config.save()

    # TODO: This should be implemented in the SiteConfigBaseClass
    def set_instance(self, site):
        try:
            self.instance = SiteConfigModel.objects.get(site=site, key=self.key)
        except ObjectDoesNotExist:
            self.instance = None

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
    key = ""  # TODO: This should be in the base class in the site-configs package.
    instance = None


    def get_initials(self):
        initial = super().get_initials()
        initial['site'] = (self.site.pk, self.site.domain)
        return initial

# Set up as a backup if the developer only want to set the processor through an enviornment variable
VENDOR_PROMO_PROCESSOR = getattr(settings, "VENDOR_PROMO_PROCESSOR", "dummy.DummyProcessor")

VENDOR_PROMO_PROCESSOR_URL = getattr(settings, "VENDOR_PROMO_PROCESSOR_URL")

VENDOR_PROMO_PROCESSOR_BARRER_KEY = getattr(settings, "VENDOR_PROMO_PROCESSOR_BARRER_KEY")
