from django.urls import path

from vendorpromo.apis.v1 import views as api_views

urlpatterns = [
    path('checkout/validate/', api_views.ValidateCodeCheckoutProcess.as_view(), name='checkout-validation'),
    path('open/validate', api_views.ValidateLinkCode.as_view(), name='open-validation'),
]