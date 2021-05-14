from vendorpromo.config import VENDOR_PROMO_PROCESSOR
from django.utils.module_loading import import_string

PromoProcessor = import_string('vendorpromo.processors.{}'.format(VENDOR_PROMO_PROCESSOR))
