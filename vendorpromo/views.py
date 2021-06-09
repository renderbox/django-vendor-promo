from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView, UpdateView
from vendor.models import Offer

from vendorpromo.forms import PromoCodeFormset
from vendorpromo.models import Promo
from vendorpromo.processors import PromoProcessor

promo_processor = PromoProcessor


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
        return redirect(request.META.get('HTTP_REFERER'))


class PromoCodeFormsetView(LoginRequiredMixin, TemplateView):
    template_name = 'vendorpromo/promocode_formset.html'

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        offer = get_object_or_404(Offer, uuid=kwargs.get('uuid'))
        formset = PromoCodeFormset(queryset=Promo.objects.filter(offer__site=offer.site, offer=offer))
        context['formset'] = formset
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        return render(request, self.template_name, context)
