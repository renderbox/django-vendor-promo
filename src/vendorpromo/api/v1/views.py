from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http.response import HttpResponse, HttpResponseBadRequest, Http404
from django.utils.translation import gettext as _
from django.views.generic import DeleteView, View

from vendor.models import Invoice
from vendor.api.v1.views import AddToCartView

from vendorpromo.forms import PromoForm
from vendorpromo.processors import get_site_promo_processor
from vendorpromo.models import Promo


class CreatePromoAPIView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        promo_form = PromoForm(request.POST)
        promo = promo_form.save(commit=False)

        if not promo_form.is_valid():
            messages.info(request, _(f'Create Promo Failed. Errors: {promo_form.errors}'))
            return redirect(request.META.get('HTTP_REFERER', "vendorpromo-list"))
            
        processor = get_site_promo_processor(promo.offer.site)(promo.offer.site)
        processor.create_promo(promo_form)
        messages.success(request, _("Promo Code Created"))
        return redirect(request.META.get('HTTP_REFERER', "vendorpromo-list"))


class DeletePromoAPIView(LoginRequiredMixin, DeleteView):
    model = Promo
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def post(self, request, *args, **kwargs):
        processor = get_site_promo_processor(self.get_object().offer.site)(self.get_object().offer.site)
        processor.delete_promo(self.get_object())
        return redirect(request.META.get('HTTP_REFERER'))


class ValidateCodeCheckoutProcessAPIView(LoginRequiredMixin, View):
    """
    When a customer is applying a code during the checkout process
    the function will check if the entered code is valid to the items
    in the cart. If valsid it will swap the Offer with the Offer that
    has that promo code. If not it will display an error message.
    In both cases it will redirect to the view that called the
    endpoint.
    """
    def post(self, request, *args, **kwargs):
        offer_in_cart = None
        try:
            invoice = get_object_or_404(Invoice, uuid=kwargs['invoice_uuid'])
            promo = get_object_or_404(Promo, code=request.POST['promo_code'], offer__site=invoice.site)
        except Http404 as error:
            messages.success(request, _("Invalid Promo Code"))
            return HttpResponseBadRequest(f"404 error: {error}")

        # loop through offers in invoice to see if any match the product form the Promo.offer instance
        for order_item in invoice.order_items.all():
            if len(promo.offer.products.all() & order_item.offer.products.all()) > 0:
                offer_in_cart = order_item.offer
                break

        if offer_in_cart is None:
            messages.success(request, _("Invalid Promo Code"))
            return HttpResponseBadRequest(f"No related offer in cart for code: {promo.code}")

        processor = get_site_promo_processor(invoice.site)(invoice.site, invoice=invoice)

        if not processor.is_code_valid_on_checkout(promo.code, promo.offer.current_price()):
            messages.success(request, _("Invalid Promo Code"))
            return HttpResponseBadRequest(f"Processor rejected code {promo.code}\nmsg:{processor.response_message}\nerror: {processor.response_error}")

        invoice.swap_offer(offer_in_cart, promo.offer)
        messages.success(request, _("Promo Code Applied"))
        return HttpResponse(_("Promo Code Applied"))


class ValidateLinkCodeAPIView(AddToCartView):
    """
    Endpoint used when a customer clicks on a link that has a promo code.
    The endpoint will validate the promo code and if valid it will add the
    corresponding offer to the cart. If invalid it will display a error
    message. In both case it will redirect to the cart view.
    params:
    code: string Promo Code
    site: int
    email: string optional for email additional validation
    return:
    redirect to cart.
    """
    def post(self, request, *args, **kwargs):
        pass
        # TODO: Need to check if the users has a session otherwise redirect to session cart.
        # try:
        #     # get Promo instance
        #     promo = Promo.objects.get(code=request.POST.get('code'))
        # except ObjectDoesNotExist:
        #     return HttpResponseNotFound(_("Invalid Promo Code"))

        # # check if site and promo.offer.site are the same
        # # if not request.site == promo.offer.site:
        #     # return HttpResponseNotFound(_("Invalid Promo Code"))

        # # initialize configured PromoProcessor
        # processor = promo_processor()

        # # validate code and redeem code through processor
        # if not processor.is_code_valid(promo.code):
        #     ## if invalid return msg error.
        #     raise HttpResponseNotFound()

        # # call redirect to vendor.views.vendor.AddToCartView (Which will redirect to the cart view)

        # csrf_token = get_token(request)
        # # csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
        # request.POST['csrf_token'] = csrf_token
        # self.kwargs['slug'] = promo.offer.slug
        # return super().post(request, args, kwargs)

