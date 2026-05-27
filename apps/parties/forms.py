from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from apps.common.form_utils import add_bootstrap_classes
from apps.common.validators import PHONE_REGEX, normalize_indian_mobile
from apps.common.services import PartyCodeService
from apps.masters.choices import PartyRoleType
from apps.parties.models import (
    BankDetail,
    CommercialProfile,
    ContactPerson,
    Party,
    PartyDocument,
    PartyRole,
    StatutoryDetail,
)


class PartyForm(forms.ModelForm):
    roles = forms.MultipleChoiceField(
        choices=PartyRoleType.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Party Roles',
    )

    class Meta:
        model = Party
        fields = [
            'name', 'email', 'mobile_no',
            'address', 'location', 'is_active',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)
        self.fields['email'].required = False
        self.fields['mobile_no'].required = False
        self.fields['mobile_no'].validators = []
        self.fields['mobile_no'].label = 'Mobile (+91)'
        self.fields['mobile_no'].widget.attrs.setdefault('placeholder', '9668123855 or +91 9668123855')
        self.fields['mobile_no'].help_text = (
            'Optional. 10-digit mobile; you may include +91 or 91 prefix.'
        )
        self.fields['name'].required = True
        self.fields['is_active'].label = 'Active'
        self.fields['is_active'].help_text = (
            'Uncheck to mark this partner inactive. The record stays in the system '
            'and can be filtered or reactivated later.'
        )
        if not self.instance.pk:
            self.fields['is_active'].initial = True
        if self.instance.pk:
            self.fields['roles'].initial = list(
                self.instance.roles.filter(is_active=True).values_list('role', flat=True)
            )

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        return email

    def clean_mobile_no(self):
        mobile = (self.cleaned_data.get('mobile_no') or '').strip()
        if not mobile:
            return ''
        digits = normalize_indian_mobile(mobile)
        if len(digits) != 10 or not PHONE_REGEX.match(digits):
            raise ValidationError(
                'Enter a valid 10-digit mobile (e.g. 9668123855 or +91 9668123855).'
            )
        return digits

    def save(self, commit=True):
        party = super().save(commit=False)
        if not party.code:
            party.code = PartyCodeService.generate_code()
        if commit:
            party.save()
            selected_roles = set(self.cleaned_data.get('roles', []))
            existing = {r.role: r for r in party.roles.all()}
            for role in selected_roles:
                if role in existing:
                    obj = existing[role]
                    if not obj.is_active:
                        obj.is_active = True
                        obj.save(update_fields=['is_active', 'updated_at'])
                else:
                    PartyRole.objects.create(party=party, role=role)
            for role, obj in existing.items():
                if role not in selected_roles and obj.is_active:
                    obj.is_active = False
                    obj.save(update_fields=['is_active', 'updated_at'])
        return party


class CommercialProfileForm(forms.ModelForm):
    class Meta:
        model = CommercialProfile
        fields = ['credit_limit', 'credit_days']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)


class StatutoryDetailForm(forms.ModelForm):
    class Meta:
        model = StatutoryDetail
        fields = [
            'cin_no', 'pan_no', 'tan_no', 'msme_no', 'esi_no', 'pf_no',
            'pan_card', 'msme_certificate', 'other_document',
        ]
        labels = {
            'cin_no': 'CIN No',
            'pan_no': 'PAN No',
            'tan_no': 'TAN No',
            'msme_no': 'MSME No',
            'esi_no': 'ESI No',
            'pf_no': 'PF No',
            'pan_card': 'PAN Card',
            'msme_certificate': 'MSME Certificate',
            'other_document': 'Other Document',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)


class BankDetailForm(forms.ModelForm):
    class Meta:
        model = BankDetail
        fields = [
            'bank_name', 'branch_name', 'account_no',
            'ifsc_code', 'micr_no', 'account_holder_name',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('DELETE'):
            return cleaned
        account_no = cleaned.get('account_no')
        party_role = cleaned.get('party_role')
        if account_no and party_role:
            qs = BankDetail.objects.filter(
                party_role=party_role,
                account_no=account_no,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    'Duplicate account number for this party role.'
                )
        return cleaned


class ContactPersonForm(forms.ModelForm):
    class Meta:
        model = ContactPerson
        fields = ['name', 'designation', 'mobile_no', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)


class PartyDocumentForm(forms.ModelForm):
    class Meta:
        model = PartyDocument
        fields = ['document_type', 'file', 'remarks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)


BankDetailFormSet = inlineformset_factory(
    PartyRole,
    BankDetail,
    form=BankDetailForm,
    extra=1,
    can_delete=True,
)

ContactPersonFormSet = inlineformset_factory(
    PartyRole,
    ContactPerson,
    form=ContactPersonForm,
    extra=1,
    can_delete=True,
)

PartyDocumentFormSet = inlineformset_factory(
    PartyRole,
    PartyDocument,
    form=PartyDocumentForm,
    extra=1,
    can_delete=True,
)


