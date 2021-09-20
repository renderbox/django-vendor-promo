from django import forms
from django.contrib.sites.models import Site
from django.db.models import TextChoices
from django.forms import fields, modelformset_factory
from django.utils.translation import ugettext as _

from vendorpromo.models import Promo

class SupportedProcessor(TextChoices):
    PROMO_CODE_BASE = ("base.PromoProcessorBase", _("Default Processor"))
    VOUCHERY = ("vouchery.VoucheryProcessor", _("Vouchery.io"))

class PromoProcessorForm(forms.Form):
    processor = forms.CharField(label=_("Processor"), widget=forms.Select(choices=SupportedProcessor.choices))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['processor'].widget = forms.Select(choices=SupportedProcessor.choices)
        self.fields['processor'].label = _("Promo Processor")

class PromoProcessorSiteSelectForm(PromoProcessorForm):
    site = forms.CharField(label=_("Site"), widget=forms.Select(choices=[(site.pk, site.domain) for site in Site.objects.all()]))


class PromoForm(forms.ModelForm):
    class Meta:
        model = Promo
        fields = [
            'description',
            'code',
            'campaign_name',
            'campaign_description',
            'meta',
            'offer']


class PromoCodeForm(forms.ModelForm):

    class Meta:
        model = Promo
        fields = ['code']


class VoucherySearchForm(forms.Form):
    querystring = forms.JSONField(required=False)
    option_params = forms.JSONField(required=False)


class PromoCodeBillingForm(forms.ModelForm):
    have_promo_code = forms.BooleanField(label=_("Do you have a promo code?"), required=False, initial=True)

    class Meta:
        model = Promo
        fields = ['code']


PromoCodeFormset = modelformset_factory(
    Promo,
    fields=['code', ],
    extra=1,
    widgets={
        'code': forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter Promo Code'
            }
        )
    }
)
