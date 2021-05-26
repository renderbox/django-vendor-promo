from django.urls import path

from vendorpromo.api.v1 import views as api_views
from vendorpromo.api.v1.vouchery import views as vouchery_api_views

urlpatterns = [
    path('checkout/validate/', api_views.ValidateCodeCheckoutProcess.as_view(), name='checkout-validation'),
    path('open/validate', api_views.ValidateLinkCode.as_view(), name='open-validation'),
    path('vouchery/campaigns', vouchery_api_views.VoucheryCampaignsView.as_view(), name='vouchery-campaigns-list'),
]
