from django import forms
from django.forms import inlineformset_factory

from apps.common.form_utils import add_bootstrap_classes
from apps.common.validators import normalize_indian_mobile
from apps.logistics.models import Truck, TruckDriver
from apps.masters.models import MarketState
from apps.transporters.models import TransporterProfile


class TransporterProfileForm(forms.ModelForm):
    class Meta:
        model = TransporterProfile
        fields = ['truck_owned_by', 'market_state']
        labels = {
            'truck_owned_by': 'Truck Owned By',
            'market_state': 'Market / State',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)
        self.fields['market_state'].queryset = MarketState.objects.filter(
            is_active=True, is_deleted=False,
        ).order_by('name')
        self.fields['market_state'].empty_label = '— Select market / state —'


class TruckForm(forms.ModelForm):
    class Meta:
        model = Truck
        fields = ['truck_number', 'truck_owner']
        labels = {
            'truck_number': 'Truck Number',
            'truck_owner': 'Truck Owner',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean_truck_number(self):
        truck_number = self.cleaned_data['truck_number']
        if truck_number:
            truck_number = truck_number.strip().upper()
            qs = Truck.objects.filter(truck_number__iexact=truck_number)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('A truck with this number already exists.')
        return truck_number


class TruckDriverForm(forms.ModelForm):
    """All driver fields optional — explicit form fields override model required flags."""

    name = forms.CharField(label='Name', max_length=150, required=False)
    aadhar_number = forms.CharField(label='Aadhar Number', max_length=12, required=False)
    phone = forms.CharField(label='Phone', max_length=20, required=False)
    dl_number = forms.CharField(label='DL Number', max_length=30, required=False)

    class Meta:
        model = TruckDriver
        fields = ['name', 'aadhar_number', 'phone', 'dl_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
            field.widget.is_required = False
            field.widget.attrs.pop('required', None)
        add_bootstrap_classes(self)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone') or ''
        if phone:
            return normalize_indian_mobile(phone)
        return ''

    def clean_aadhar_number(self):
        import re
        aadhar = self.cleaned_data.get('aadhar_number') or ''
        if aadhar:
            return re.sub(r'\D', '', aadhar)
        return ''

    def clean_dl_number(self):
        return (self.cleaned_data.get('dl_number') or '').strip()

    def clean_name(self):
        return (self.cleaned_data.get('name') or '').strip()


class BaseTruckDriverFormSet(forms.BaseInlineFormSet):
    """Skip completely empty driver rows; allow partial data (e.g. name only)."""

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        for form in self.forms:
            if not hasattr(form, 'cleaned_data') or not form.cleaned_data:
                continue
            if form.cleaned_data.get('DELETE'):
                continue
            if form.instance.pk:
                continue
            if not driver_row_has_data(form.cleaned_data):
                form.cleaned_data['DELETE'] = True


def driver_row_has_data(cleaned):
    return any([
        (cleaned.get('name') or '').strip(),
        (cleaned.get('aadhar_number') or '').strip(),
        (cleaned.get('phone') or '').strip(),
        (cleaned.get('dl_number') or '').strip(),
    ])


# Backward-compatible alias used in views
_driver_row_has_data = driver_row_has_data


TruckFormSet = inlineformset_factory(
    TransporterProfile,
    Truck,
    form=TruckForm,
    extra=1,
    can_delete=True,
)

TruckDriverFormSet = inlineformset_factory(
    Truck,
    TruckDriver,
    form=TruckDriverForm,
    formset=BaseTruckDriverFormSet,
    extra=1,
    can_delete=True,
    validate_min=False,
    min_num=0,
)
