from django.views.generic import TemplateView, FormView

from vendorpromo.forms import PromoForm


class DjangoVendorPromoIndexView(TemplateView):
    template_name = "core/index.html"


class EnterPromoCode(TemplateView):
    template_name = "core/enter_code.html"


class VoucheryCreatePromoOffer(FormView, TemplateView):
    template_name = "core/offer_promo_create.html"
    form_class = PromoForm

