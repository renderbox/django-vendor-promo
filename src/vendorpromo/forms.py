from django import forms
from django.contrib.sites.models import Site
from django.db.models import TextChoices
from django.forms import modelformset_factory
from django.utils.translation import gettext as _

from integrations.models import Credential
from vendorpromo.models import Affiliate, Promo, PromotionalCampaign, CouponCode

from vendor.models import CustomerProfile
from vendor.models.base import get_product_model


class AffiliateForm(forms.ModelForm):
    customer_profile = forms.ModelChoiceField(queryset=CustomerProfile.objects.all(), required=False)
    
    class Meta:
        model = Affiliate
        fields = ['slug', 'customer_profile', 'contact_name', 'email', 'company']

    def __init__(self, *args, **kwargs):
        site = kwargs.pop('site', None)
        super().__init__(*args, **kwargs)

        if site:
            self.fields['customer_profile'].queryset = CustomerProfile.objects.filter(site=site)


class SupportedPromoProcessor(TextChoices):
    PROMO_CODE_BASE = ("base.PromoProcessorBase", _("Default Processor"))
    VOUCHERY = ("vouchery.VoucheryProcessor", _("Vouchery.io"))


class PromoProcessorForm(forms.Form):
    promo_processor = forms.CharField(label=_("Processor"), widget=forms.Select(choices=SupportedPromoProcessor.choices))


class PromoProcessorSiteSelectForm(PromoProcessorForm):
    site = forms.CharField(label=_("Site"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['site'].widget = forms.Select(choices=[(site.pk, site.domain) for site in Site.objects.all()])

# To be deprecated
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

# To be deprecated
class PromoCodeForm(forms.ModelForm):

    class Meta:
        model = Promo
        fields = ['code']


class PromotionalCampaignForm(forms.ModelForm):
    applys_to = forms.ModelMultipleChoiceField(queryset=get_product_model().objects.all(), required=False)
    is_percent_off = forms.NullBooleanField(widget=forms.RadioSelect(
        choices=[
            (True, "Percent Off"),
            (False, "Fixed Amount")
        ]
    ))
    discount_value = forms.DecimalField(min_value=0, label=_("Discount Value"), required=False)

    class Meta:
        model = PromotionalCampaign
        fields = [
            "campaign_id",
            "name",
            "description",
            "start_date",
            "end_date",
            "max_redemptions",
        ]

    def __init__(self, *args, **kwargs):
        site = kwargs.pop('site', None)
        super().__init__(*args, **kwargs)

        if site:
            self.fields['applys_to'].queryset = get_product_model().objects.filter(site=site)

        if self.instance.pk:
            self.fields['applys_to'].initial = self.instance.applys_to.products.all()
            self.fields['is_percent_off'].initial = (True, "Percent Off") if self.instance.is_percent_off else (False, "Fixed Amount")
            self.fields['discount_value'].initial = self.instance.applys_to.current_price()

    def clean_discount_value(self):
        discount_value = self.cleaned_data.get('discount_value', 0)

        if discount_value <= 0:
            raise forms.ValidationError(_("Number must be greater than 0"))
        
        if self.cleaned_data.get('is_percent_off'):
            if discount_value < 0 or self.cleaned_data.get('discount_value') > 100:
                raise forms.ValidationError(_("Must be a number between 0 and 100"))
        
        return discount_value


class CouponCodeForm(forms.ModelForm):

    class Meta:
        model = CouponCode
        fields = [
            "code",
            "max_redemptions",
            "end_date",
            "promo"
        ]

    def __init__(self, *args, **kwargs):
        self.site = kwargs.pop('site', None)

        super().__init__(*args, **kwargs)

        if self.site:
            self.fields['promo'].queryset = PromotionalCampaign.objects.filter(site=self.site)

    def clean_code(self):
        code = self.cleaned_data['code']
        promo = self.data['promo']

        if PromotionalCampaign.objects.filter(pk=promo, coupon__code=code, site=self.site).exists():
            raise forms.ValidationError(_("Code already exists"))
        
        return code


CouponCodeFormset = modelformset_factory(CouponCode, CouponCodeForm, extra=1)


class VoucherySearchForm(forms.Form):
    querystring = forms.JSONField(required=False)
    option_params = forms.JSONField(required=False)


class PromoCodeBillingForm(forms.ModelForm):
    have_promo_code = forms.BooleanField(label=_("Do you have a promo code?"), required=False, initial=True)

    class Meta:
        model = Promo
        fields = ['code']


# To be deprecated
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


class VoucheryIntegrationForm(forms.ModelForm):
    class Meta:
        model = Credential
        fields = ['client_url', 'private_key']
        labels = {
            'client_url': "Vouchery URL",
            'private_key': "Vouchery Barrer Key"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client_url'].required = True
        self.fields['private_key'].required = True
