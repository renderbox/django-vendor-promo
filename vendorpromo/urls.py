from django.urls import path

from vendorpromo import views

urlpatterns = [
    path("", views.DjangoVendorPromoIndexView.as_view(), name="vendorpromo-list"),
    path("promo/create", views.PromoCreateView.as_view(), name="vendorpromo-create"),
    path("promo/<str:uuid>/update", views.PromoUpdateView.as_view(), name="vendorpromo-update"),
    path("promo/<str:uuid>/delete", views.PromoDeleteView.as_view(), name="vendorpromo-delete"),
    path("offer/<str:uuid>/promocodes/", views.PromoCodeFormsetView.as_view(), name="vendorpromo-promocode-formset"),
    path("processors/", views.PromoCodeSiteConfigsListView.as_view(), name="vendorpromo-processor-lists"),
    path("processor/siteconfig/", views.PromoProcessorFormView.as_view(), name="vendorpromo-processor"),
    path("processor/siteconfig/<int:pk>/site/", views.PromoProcessorSiteSelectFormView.as_view(), name="vendorpromo-processor-site"),
    path("vouchery/integration/", views.VoucheryIntegrationView.as_view(), name="vouchery-integration"),
]
