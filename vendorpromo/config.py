# App Settings
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

from siteconfigs.config import SiteConfigBaseClass
from vendorpromo.forms import PromoCodeProcessorForm


class PromoCodeProcessor(SiteConfigBaseClass):
    label = _("Promo Code Processor")
    default = {"processor": "base.PromoProcessorBase"}
    form_class = PromoCodeProcessorForm

    def __init__(self):
        site = Site.objects.get_current()
        self.key = ".".join([__name__, __class__.__name__])
        super().__init__(site, self.key)

# Set up as a backup if the developer only want to set the processor through an enviornment variable
VENDOR_PROMO_PROCESSOR = getattr(settings, "VENDOR_PROMO_PROCESSOR", "dummy.DummyProcessor")

VENDOR_PROMO_PROCESSOR_URL = getattr(settings, "VENDOR_PROMO_PROCESSOR_URL")

VENDOR_PROMO_PROCESSOR_BARRER_KEY = getattr(settings, "VENDOR_PROMO_PROCESSOR_BARRER_KEY")
