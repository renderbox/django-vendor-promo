from django.views.generic import TemplateView


class DjangoVendorPromoIndexView(TemplateView):
    template_name = "vendorpromo/index.html"
