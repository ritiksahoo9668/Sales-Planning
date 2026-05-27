from django.contrib import admin

from .models import MarketState, VendorCategory, VendorSubCategory, VendorType


class VendorSubCategoryInline(admin.TabularInline):
    model = VendorSubCategory
    extra = 1
    fields = ('name', 'description', 'is_active')


@admin.register(VendorType)
class VendorTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('is_active',)
    ordering = ('name',)


@admin.register(VendorCategory)
class VendorCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)
    inlines = [VendorSubCategoryInline]


@admin.register(VendorSubCategory)
class VendorSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active')
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'is_active')
    autocomplete_fields = ('category',)


@admin.register(MarketState)
class MarketStateAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    search_fields = ('name', 'code')
