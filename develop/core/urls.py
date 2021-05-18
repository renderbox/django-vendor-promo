from django.urls import path

from . import views

urlpatterns = [
    path("", views.EnterPromoCode.as_view(), name="vendorpromo-index"),
]
