from django.urls import path

from vendorpromo.apis.v1 import views as api_views

urlpatterns = [
    path('', api_views.VendorPromoIndexAPI.as_view(), name='api-index'),
]