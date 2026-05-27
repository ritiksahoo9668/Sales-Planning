from django.contrib import admin

from apps.logistics.models import Truck, TruckDriver

from .models import TransporterProfile


class TruckDriverInline(admin.TabularInline):
    model = TruckDriver
    extra = 0


class TruckInline(admin.TabularInline):
    model = Truck
    extra = 0
    show_change_link = True


@admin.register(TransporterProfile)
class TransporterProfileAdmin(admin.ModelAdmin):
    list_display = ('party_role', 'market_state', 'truck_owned_by', 'is_active')
    search_fields = ('party_role__party__name', 'party_role__party__code')
    list_filter = ('truck_owned_by', 'market_state', 'is_active')
    inlines = [TruckInline]


@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ('truck_number', 'transporter', 'truck_owner', 'is_active')
    search_fields = ('truck_number', 'truck_owner', 'transporter__party_role__party__name')
    list_filter = ('is_active',)
    inlines = [TruckDriverInline]


@admin.register(TruckDriver)
class TruckDriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'truck', 'phone', 'dl_number', 'is_active')
    search_fields = ('name', 'phone', 'dl_number', 'aadhar_number', 'truck__truck_number')
    list_filter = ('is_active',)
