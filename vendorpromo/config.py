# App Settings
from django.conf import settings

VENDOR_PROMO_PROCESSOR = getattr(settings, "VENDOR_PROMO_PROCESSOR", "dummy.DummyProcessor")

VENDOR_PROMO_PROCESSOR_URL = getattr(settings, "VENDOR_PROMO_PROCESSOR_URL")

VENDOR_PROMO_PROCESSOR_BARRER_KEY = getattr(settings, "VENDOR_PROMO_PROCESSOR_BARRER_KEY")
