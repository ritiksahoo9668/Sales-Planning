from django.contrib import admin

from .models import VendorProfile


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = (
        'company_name',
        'party_role',
        'vendor_type',
        'vendor_category',
        'office_status',
        'gst_no',
        'is_active',
    )
    search_fields = ('company_name', 'gst_no', 'party_role__party__name', 'party_role__party__code')
    list_filter = ('vendor_type', 'office_status', 'vendor_category', 'is_active')
    raw_id_fields = ('party_role', 'vendor_type', 'vendor_category', 'vendor_sub_category')
    autocomplete_fields = ('vendor_type', 'vendor_category', 'vendor_sub_category')
