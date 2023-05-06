from django.contrib import admin

from vendorpromo.models import Affiliate, Promo


###############
# MODEL ADMINS
###############
class PromoAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid',)
    list_display = ('code', 'offer', 'slug')
    search_fields = ('code', 'offer', )


class AffiliateAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', )
    list_display = ('customer_profile', 'slug', 'full_name', 'email', 'company')
    search_fields = ('full_name', 'email', 'company', 'slug')
    list_filter = ('customer_profile__site', )


###############
# REGISTRATION
###############
admin.site.register(Promo, PromoAdmin)
admin.site.register(Affiliate, AffiliateAdmin)
