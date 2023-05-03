from vendorpromo.utils import get_site_from_request

class SiteOnRequestFilterMixin:

    def get_queryset(self):
        if hasattr(self.request, 'site'):
            return self.model.objects.filter(site=get_site_from_request(self.request))
        return self.model.on_site.all()