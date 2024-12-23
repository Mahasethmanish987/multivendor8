from django.contrib import admin
from .models import Vendor,OpeningHour

# Register your models here.
class VendorAdmin(admin.ModelAdmin):
    list_display=('vendor_name','user__email','is_approved','created_at')
    list_editable=('is_approved',)
    # list_editable=('is_approved',)

class OpeningHourAdmin(admin.ModelAdmin):
    list_display=('vendor','day','from_hour','to_hour','is_closed')
    list_display_links=('vendor',)

admin.site.register(Vendor,VendorAdmin)
admin.site.register(OpeningHour,OpeningHourAdmin)