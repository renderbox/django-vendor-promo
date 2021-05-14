from django.urls import path

from vendorpromo import views

urlpatterns = [
    path("", views.DjangoVendorPromoIndexView.as_view(), name="vendorpromo-list"),
    path("promo/create", views.PromoCreateView.as_view(), name="vendorpromo-create"),
    path("promo/<str:uuid>/update", views.PromoUpdateView.as_view(), name="vendorpromo-update"),
]
