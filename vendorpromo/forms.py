from django import forms
from vendorpromo.models import Promo


class PromoFrom(forms.ModelForm):
    class Meta:
        model = Promo
        fields = [
            'name',
            'description',
            'code',
            'campaign_name',
            'campaign_description',
            'meta',
            'offer']


class VoucherySearchForm(forms.Form):
    querystring = forms.JSONField(required=False)
    option_params = forms.JSONField(required=False)
