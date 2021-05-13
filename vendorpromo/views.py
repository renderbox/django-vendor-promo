from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView
from django.views.generic.edit import UpdateView

from vendor.models import Offer
from vendorpromo.models import Promo


class DjangoVendorPromoIndexView(TemplateView):
    template_name = "vendorpromo/index.html"


class PromoCreateView(LoginRequiredMixin, CreateView):
    template_name = 'vendorpromo/promo.html'
    model = Promo
    fields = ('__all__')

    def get_initial(self):
        return {'offer': Offer.objects.filter(site=self.request.site)}


class PromoUpdateView(LoginRequiredMixin, UpdateView):
    model = Promo

    def get_initial(self):
        return {'offer': Offer.objects.filter(site=self.request.site)}

