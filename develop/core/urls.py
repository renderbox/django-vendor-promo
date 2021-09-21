from django.urls import path

from core import views

urlpatterns = [
    path("", views.EnterPromoCode.as_view(), name="vendorpromo-index"),
    path("buy/", views.OfferListPurchaseListView.as_view(), name="vendorpromo-buy"),
    path("vouchery/promo/create/", views.VoucheryCreatePromoOffer.as_view(), name="core-promo-create"),
]
