from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('core.urls')),
    path('api/', include('vendorpromo.api.v1.urls')),
    path('vendorpromo/', include('vendorpromo.urls') ),
    path('vendor/', include('vendor.urls.vendor')),
    path('vendor/manage/', include('vendor.urls.vendor_admin')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('siteconfigs/', include('siteconfigs.urls')),
]
