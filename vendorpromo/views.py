from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import CreateView, ListView
from django.views.generic.edit import UpdateView

from vendor.models import Offer
from vendorpromo.models import Promo


class DjangoVendorPromoIndexView(LoginRequiredMixin, ListView):
    template_name = "vendorpromo/promo_list.html"
    model = Promo


class PromoCreateView(LoginRequiredMixin, CreateView):
    template_name = 'vendorpromo/promo.html'
    model = Promo
    fields = ('__all__')

    def get_initial(self):
        # TODO: Still need to see how I can get the site from the request
        return {'offer': Offer.objects.filter(site=self.request.user.customer_profile.first().site)}

    def form_valid(self, form):
        promo = form.save(commit=False)

        promo.save()
        return redirect('vendorpromo-list')


class PromoUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'vendorpromo/promo.html'
    model = Promo
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    fields = ('__all__')

    def form_valid(self, form):
        promo = form.save(commit=False)
        promo.save()
        return redirect('vendorpromo-list')
