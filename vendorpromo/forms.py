from django.forms import ModelForm
from vendorpromo.models import Promo


class PromoFrom(ModelForm):
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
