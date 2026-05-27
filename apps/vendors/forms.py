from django import forms

from apps.common.form_utils import add_bootstrap_classes
from apps.masters.choices import OfficeStatus
from apps.masters.models import VendorCategory, VendorSubCategory, VendorType

from .models import VendorProfile


class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = [
            'company_name', 'vendor_type', 'vendor_category', 'vendor_sub_category',
            'office_status', 'gst_no', 'dispatch_location',
        ]
        labels = {
            'company_name': 'Company Name',
            'vendor_type': 'Vendor Type',
            'vendor_category': 'Vendor Category',
            'vendor_sub_category': 'Vendor Sub Category',
            'office_status': 'Office Status',
            'gst_no': 'GST No',
            'dispatch_location': 'Dispatch Location',
        }
        widgets = {
            'office_status': forms.Select(attrs={'class': 'form-select'}),
            'dispatch_location': forms.TextInput(attrs={'placeholder': 'City / plant / warehouse'}),
            'gst_no': forms.TextInput(attrs={'placeholder': 'e.g. 27AAAAA0000A1Z5'}),
            'company_name': forms.TextInput(attrs={'placeholder': 'Legal / trade name'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

        master_fields = ('vendor_type', 'vendor_category', 'vendor_sub_category')
        for name in master_fields:
            self.fields[name].empty_label = f'— Select {self.fields[name].label.lower()} —'
            self.fields[name].queryset = self.fields[name].queryset.model.objects.filter(
                is_active=True, is_deleted=False
            )

        self.fields['vendor_type'].queryset = VendorType.objects.filter(
            is_active=True, is_deleted=False
        ).order_by('name')
        self.fields['vendor_category'].queryset = VendorCategory.objects.filter(
            is_active=True, is_deleted=False
        ).order_by('name')

        category_id = self.data.get('vendor_category') if self.data else None
        if not category_id and self.instance.pk and self.instance.vendor_category_id:
            category_id = self.instance.vendor_category_id

        sub_qs = VendorSubCategory.objects.filter(
            is_active=True, is_deleted=False
        ).select_related('category').order_by('category__name', 'name')
        if category_id:
            sub_qs = sub_qs.filter(category_id=category_id)
        self.fields['vendor_sub_category'].queryset = sub_qs

        if 'office_status' in self.fields:
            self.fields['office_status'].choices = OfficeStatus.choices

    def clean(self):
        cleaned = super().clean()
        category = cleaned.get('vendor_category')
        sub = cleaned.get('vendor_sub_category')
        if sub and category and sub.category_id != category.id:
            raise forms.ValidationError({
                'vendor_sub_category': 'Sub category must belong to the selected vendor category.',
            })
        return cleaned
