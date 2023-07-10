from django.contrib import admin

from vendorpromo.models import Affiliate, PromotionalCampaign, CouponCode, Promo
from vendor.models import CustomerProfile, Offer


###############
# MODEL ADMINS
###############
class PromoAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid',)
    list_display = ('code', 'offer', 'slug')
    search_fields = ('code', 'offer', )


class AffiliateAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', 'customer_profile')
    list_display = ('customer_profile', 'slug', 'contact_name', 'email', 'company')
    search_fields = ('contact_name', 'email', 'company', 'slug')
    list_filter = ('customer_profile__site', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "customer_profile" and hasattr(request, 'site'):
            kwargs["queryset"] = CustomerProfile.objects.filter(site=request.site)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PromotionalCampaignAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid',)
    list_display = ('name', 'site')
    search_fields = ('name',)
    list_filter = ('site',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "applies_to" and hasattr(request, 'site'):
            kwargs["queryset"] = Offer.objects.filter(site=request.site)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CouponCodeAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', 'invoice')
    list_display = ('code', 'promo')
    search_fields = ('code', 'promo__name')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "promo" and hasattr(request, 'site'):
            kwargs["queryset"] = PromotionalCampaign.objects.filter(site=request.site)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

###############
# REGISTRATION
###############
admin.site.register(Promo, PromoAdmin)
admin.site.register(Affiliate, AffiliateAdmin)
admin.site.register(PromotionalCampaign, PromotionalCampaignAdmin)
admin.site.register(CouponCode, CouponCodeAdmin)
