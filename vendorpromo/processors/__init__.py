from django.utils.module_loading import import_string
from django.core.exceptions import ObjectDoesNotExist
from vendorpromo.config import ProcessorSiteConfig, VENDOR_PROMO_PROCESSOR
from siteconfigs.models import SiteConfigModel


def get_site_promo_processor(site):
    site_processor = ProcessorSiteConfig()
    try:
        return import_string(f"vendorpromo.processors.{SiteConfigModel.objects.get(site=site, key=site_processor.key).value}")
    except ObjectDoesNotExist:
        # Should it return the default if not found?
        # raise ValueError("PromoProcessor has not been configured")
        return import_string(f"vendorpromo.processors.{SiteConfigModel.objects.get(site=site, key=site_processor.key).value}")