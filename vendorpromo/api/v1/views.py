from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseNotFound
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views import View

from vendor.views.vendor import AddToCartView

from vendorpromo.processors import PromoProcessor
from vendorpromo.models import Promo


promo_processor = PromoProcessor


class ValidateCodeCheckoutProcess(LoginRequiredMixin, View):
    """
    When a customer is applying a code during the checkout process
    the function will check if the entered code is valid to the items
    in the cart. If valsid it will swap the Offer with the Offer that
    has that promo code. If not it will display an error message.
    In both cases it will redirect to the view that called the
    endpoint.
    """
    def post(self, request, *args, **kwargs):
        # get Invoice instance
        # get Promo instance
        # loop through offers in invoice to see if any match the product form the Promo.offer instance
        ## if yes keep that invoice.offer
        ## if no return msg error.
        # initialize configured PromoProcessor
        # validate code and redeem code through processor
        ## if invalid return msg error.
        # call invoice.swap(original_offer, promo.offer)
        return redirect(request.META.get('HTTP_REFERER', "vendor:cart"))


class ValidateLinkCode(AddToCartView):
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
        # Should code be unique to sites, I am guessing yes. 
        try:
            promo = Promo.objects.get(code=request.POST.get('code'))
        except ObjectDoesNotExist:
            return HttpResponseNotFound(_("Invalid Promo Code"))
        # get Promo instance
        # check if site and promo.offer.site are the same
        # initialize configured PromoProcessor
        # validate code and redeem code through processor
        ## if invalid return msg error.
        # call redirect to vendor.views.vendor.AddToCartView (Which will redirect to the cart view)
        return super().post(request, *args, kwargs={"slug": promo.offer.slug})
