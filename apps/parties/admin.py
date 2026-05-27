from django.contrib import admin

from .models import (
    BankDetail,
    BrokerProfile,
    CommercialProfile,
    ContactPerson,
    CustomerProfile,
    Party,
    PartyDocument,
    PartyRole,
    StatutoryDetail,
)


class PartyRoleInline(admin.TabularInline):
    model = PartyRole
    extra = 0
    fields = ('role', 'is_active')


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'mobile_no', 'location', 'is_active', 'created_at')
    search_fields = ('code', 'name', 'email', 'mobile_no', 'phone')
    list_filter = ('is_active', 'location', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PartyRoleInline]


class BankDetailInline(admin.TabularInline):
    model = BankDetail
    extra = 0


class ContactPersonInline(admin.TabularInline):
    model = ContactPerson
    extra = 0


class PartyDocumentInline(admin.TabularInline):
    model = PartyDocument
    extra = 0


@admin.register(PartyRole)
class PartyRoleAdmin(admin.ModelAdmin):
    list_display = ('party', 'role', 'is_active', 'created_at')
    search_fields = ('party__code', 'party__name', 'role')
    list_filter = ('role', 'is_active')
    inlines = [BankDetailInline, ContactPersonInline, PartyDocumentInline]


@admin.register(CommercialProfile)
class CommercialProfileAdmin(admin.ModelAdmin):
    list_display = ('party_role', 'credit_limit', 'credit_days', 'is_active')
    search_fields = ('party_role__party__name',)
    list_filter = ('is_active',)


@admin.register(BankDetail)
class BankDetailAdmin(admin.ModelAdmin):
    list_display = ('party_role', 'bank_name', 'account_no', 'ifsc_code', 'is_active')
    search_fields = ('bank_name', 'account_no', 'ifsc_code', 'party_role__party__name')
    list_filter = ('is_active', 'bank_name')


@admin.register(StatutoryDetail)
class StatutoryDetailAdmin(admin.ModelAdmin):
    list_display = ('party_role', 'pan_no', 'gst_display', 'is_active')
    search_fields = ('pan_no', 'cin_no', 'party_role__party__name')

    @admin.display(description='Party')
    def gst_display(self, obj):
        return obj.party_role.party.name


@admin.register(ContactPerson)
class ContactPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'party_role', 'designation', 'mobile_no', 'email')
    search_fields = ('name', 'email', 'mobile_no', 'party_role__party__name')
    list_filter = ('is_active',)


@admin.register(PartyDocument)
class PartyDocumentAdmin(admin.ModelAdmin):
    list_display = ('party_role', 'document_type', 'created_at', 'is_active')
    search_fields = ('party_role__party__name', 'remarks')
    list_filter = ('document_type', 'is_active')


admin.site.register(BrokerProfile)
admin.site.register(CustomerProfile)
