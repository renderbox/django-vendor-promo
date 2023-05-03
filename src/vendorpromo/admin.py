from django.contrib import admin

from vendorpromo.models import Promo


###############
# MODEL ADMINS
###############
class PromoAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid',)
    list_display = ('code', 'offer', 'slug')
    search_fields = ('code', 'offer', )


###############
# REGISTRATION
###############
admin.site.register(Promo, PromoAdmin)
