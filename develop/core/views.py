from django.views.generic import TemplateView, FormView, ListView

from vendor.models import Offer
from vendor.utils import get_site_from_request

from vendorpromo.forms import PromoForm


class DjangoVendorPromoIndexView(TemplateView):
    template_name = "core/index.html"


class OfferListPurchaseListView(ListView):
    template_name = "core/offers_purchase.html"
    model = Offer

    def get_queryset(self):
        if hasattr(self.request, 'site'):
            return self.model.objects.filter(site=get_site_from_request(self.request))
        return self.model.on_site.all()


class EnterPromoCode(TemplateView):
    template_name = "core/enter_code.html"


class VoucheryCreatePromoOffer(FormView, TemplateView):
    template_name = "core/offer_promo_create.html"
    form_class = PromoForm
