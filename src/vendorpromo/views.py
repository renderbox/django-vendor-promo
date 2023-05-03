from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView, FormMixin, UpdateView, FormView

from vendor.models import Offer
from vendorpromo.config import PromoProcessorSiteConfig, PromoProcessorSiteSelectSiteConfig
from vendorpromo.forms import PromoCodeFormset, PromoProcessorForm, PromoProcessorSiteSelectForm, VoucheryIntegrationForm
from vendorpromo.integrations import VoucheryIntegration
from vendorpromo.models import Promo
from vendorpromo.processors import get_site_promo_processor
from vendorpromo.utils import get_site_from_request

from siteconfigs.models import SiteConfigModel


class DjangoVendorPromoIndexView(LoginRequiredMixin, ListView):
    template_name = "vendorpromo/promo_list.html"
    model = Promo


class PromoCodeSiteConfigsListView(ListView):
    template_name = 'vendorpromo/processor_site_config_list.html'
    model = SiteConfigModel

    def get_queryset(self):
        promo_processor = PromoProcessorSiteConfig()
        return SiteConfigModel.objects.filter(key=promo_processor.key)


class PromoProcessorFormView(FormView):
    template_name = 'vendorpromo/processor_site_config.html'
    form_class = PromoProcessorForm

    def get_success_url(self):
        return reverse('vendorpromo-processor')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        processor_config = PromoProcessorSiteConfig()
        context['form'] = processor_config.get_form()
        return context

    def form_valid(self, form):
        processor_config = PromoProcessorSiteConfig()
        processor_config.save(form.cleaned_data["promo_processor"], "promo_processor")
        return redirect('vendorpromo-processor-lists')


class PromoProcessorSiteSelectFormView(FormView):
    template_name = 'vendorpromo/processor_site_config.html'
    form_class = PromoProcessorSiteSelectForm

    def get_success_url(self):
        return reverse('vendorpromo-processor')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        processor_config = PromoProcessorSiteSelectSiteConfig(Site.objects.get(pk=self.kwargs.get('pk')))
        context['form'] = processor_config.get_form()
        return context

    def form_valid(self, form):
        site = Site.objects.get(pk=form.cleaned_data['site'])
        processor_config = PromoProcessorSiteSelectSiteConfig(site)
        processor_config.save(form.cleaned_data["promo_processor"], "promo_processor")
        return redirect('vendorpromo-processor-lists')


class PromoCreateView(LoginRequiredMixin, CreateView):
    template_name = 'vendorpromo/promo.html'
    model = Promo
    fields = ('__all__')

    def get_initial(self):
        # TODO: Still need to see how I can get the site from the request
        return {'offer': Offer.objects.filter(site=self.request.user.customer_profile.first().site)}

    def form_valid(self, form):
        promo = form.save(commit=False)
        processor = get_site_promo_processor(promo.offer.site)(promo.offer.site)
        processor.create_promo(form)
        return redirect('vendorpromo-list')


class PromoUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'vendorpromo/promo.html'
    model = Promo
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    fields = ('__all__')

    def form_valid(self, form):
        promo = form.save(commit=False)
        processor = get_site_promo_processor(promo.offer.site)(promo.offer.site)
        processor.update_promo(form)
        return redirect('vendorpromo-list')


class PromoDeleteView(LoginRequiredMixin, DeleteView):
    model = Promo
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def post(self, request, *args, **kwargs):
        processor = get_site_promo_processor(self.get_object().offer.site)(self.get_object().offer.site)
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


class VoucheryIntegrationView(FormView):
    template_name = "vendorpromo/vouchery_integration.html"
    form_class = VoucheryIntegrationForm
    success_url = reverse_lazy('vouchery-integration')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        vouchery_integration = VoucheryIntegration(get_site_from_request(self.request))
        if vouchery_integration.instance:
            context['form'] = VoucheryIntegrationForm(instance=vouchery_integration.instance)
        else:
            context['form'] = VoucheryIntegrationForm()
        return context
    
    def form_valid(self, form):
        vouchery_integration = VoucheryIntegration(get_site_from_request(self.request))
        vouchery_integration.save(form.cleaned_data)
        return super().form_valid(form)
