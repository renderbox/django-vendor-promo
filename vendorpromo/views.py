from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import CreateView, ListView
from django.views.generic.edit import DeleteView, UpdateView
from vendor.models import Offer
from vendorpromo.models import Promo
from vendorpromo.config import VENDOR_PROMO_PROCESSOR

promo_processor = VENDOR_PROMO_PROCESSOR


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
        processor = promo_processor()
        processor.create_promo(form)
        return redirect('vendorpromo-list')


class PromoUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'vendorpromo/promo.html'
    model = Promo
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    fields = ('__all__')

    def form_valid(self, form):
        processor = promo_processor()
        processor.update_promo(form)
        return redirect('vendorpromo-list')


class PromoDeleteView(LoginRequiredMixin, DeleteView):
    model = Promo
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def post(self, request, *args, **kwargs):
        processor = promo_processor()
        processor.delete_promo(self.get_object())
        return redirect('vendorpromo-list')


