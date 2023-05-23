from django.utils.module_loading import import_string
from django.core.exceptions import ObjectDoesNotExist
from vendorpromo.config import PromoProcessorSiteConfig
from siteconfigs.models import SiteConfigModel


def get_site_promo_processor(site):
    site_processor = PromoProcessorSiteConfig(site)
    return import_string(f"vendorpromo.processors.{site_processor.get_key_value('promo_processor')}")
