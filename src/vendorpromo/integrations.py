from django.core.exceptions import ObjectDoesNotExist
from vendorpromo.forms import VoucheryIntegrationForm
from integrations.models import Credential


def get_available_integrations():
    return [VoucheryIntegration, ]


def get_integration_instance(site, name):
    available_integrations = [integration(site) for integration in get_available_integrations()]
    for integration in available_integrations:
        if integration.name == name:
            return integration
    return None


class VoucheryIntegration(object):
    NAME = "Vouchery Integration"

    site = None
    form_class = VoucheryIntegrationForm

    def __init__(self, site):
        self.site = site
        self.instance = self.get_instance()

    def get_instance(self):
        try:
            return Credential.objects.get(name=self.NAME, site=self.site)
        except ObjectDoesNotExist:
            return None
    
    def save(self, data):
        if not self.instance:
            form = self.form_class(data)
        else:
            form = self.form_class(data, instance=self.instance)
        
        vouchery = form.save(commit=False)
        vouchery.name = self.NAME
        vouchery.site = self.site
        vouchery.save()
    
    