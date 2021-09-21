from django.utils.module_loading import import_string
from django.core.exceptions import ObjectDoesNotExist
from vendorpromo.config import PromoProcessorSiteConfig
from siteconfigs.models import SiteConfigModel


def get_site_promo_processor(site):
    site_processor = PromoProcessorSiteConfig()
    try:
        return import_string(f"vendorpromo.processors.{SiteConfigModel.objects.get(site=site, key=site_processor.key).value['promo_processor']}")
    except ObjectDoesNotExist:
        # Should it return the default if not found?
        # raise ValueError("PromoProcessor has not been configured")
        return import_string(f"vendorpromo.processors.{site_processor.default['promo_processor']}")
