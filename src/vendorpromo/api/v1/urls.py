from django.urls import path

from vendorpromo.api.v1 import views as api_views
from vendorpromo.api.v1.vouchery import views as vouchery_api_views

urlpatterns = [
    path('checkout/validate/<str:invoice_uuid>', api_views.ValidateCodeCheckoutProcessAPIView.as_view(), name='checkout-validation'),
    path('open/validate', api_views.ValidateLinkCodeAPIView.as_view(), name='open-validation'),
    path('delete/<str:uuid>', api_views.DeletePromoAPIView.as_view(), name='api-promo-delete'),

    path('vouchery/promo/autocreate', vouchery_api_views.VoucheryCreateOfferPromoAPIView.as_view(), name='vouchery-promo-autocreate'),
    path('vouchery/campaigns', vouchery_api_views.VoucheryCampaignsView.as_view(), name='vouchery-campaigns-list'),
    path('vouchery/campaign/<int:campaign_id>', vouchery_api_views.VoucheryCampaignDetailView.as_view(), name='vouchery-campaigns-list'),
    path('vouchery/campaign/<int:campaign_id>/redeemed', vouchery_api_views.VoucheryRedeemListView.as_view(), name='vouchery-campaigns-redeemed'),
    path('vouchery/redeem/<str:code>/detail/<str:transaction_id>', vouchery_api_views.VoucheryRedeemDetailView.as_view(), name='vouchery-redeem-detail'),
    path('vouchery/vouchers/<int:campaign_id>', vouchery_api_views.VoucheryVouchersView.as_view(), name='vouchery-voucher-list'),
    path('vouchery/voucher/<str:code>', vouchery_api_views.VoucheryVoucherDetailView.as_view(), name='vouchery-voucher-detail'),
]
