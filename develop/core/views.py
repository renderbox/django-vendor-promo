from django.views.generic import TemplateView, FormView

from vendor.models import Offer
from vendorpromo.forms import PromoForm


class DjangoVendorPromoIndexView(TemplateView):
    template_name = "core/index.html"


class EnterPromoCode(TemplateView):
    template_name = "core/enter_code.html"


class VoucheryCreatePromoOffer(FormView, TemplateView):
    template_name = "core/offer_promo_create.html"
    form_class = PromoForm

    # def get_context_data(self, *args, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context
