from django.core.exceptions import ValidationError
from django.db import models

from apps.common.validators import validate_gst, validate_ifsc, validate_mobile, validate_pan
from apps.core.models import BaseERPModel
from apps.masters.choices import DocumentType, PartyRoleType


class Party(BaseERPModel):
    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    mobile_no = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = 'Parties'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'is_active']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return f'{self.code} - {self.name}'


class PartyRole(BaseERPModel):
    party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        related_name='roles',
    )
    role = models.CharField(
        max_length=20,
        choices=PartyRoleType.choices,
        db_index=True,
    )

    class Meta:
        ordering = ['role']
        constraints = [
            models.UniqueConstraint(
                fields=['party', 'role'],
                name='unique_party_role_per_party',
            ),
        ]
        indexes = [
            models.Index(fields=['party', 'role', 'is_active']),
        ]

    def __str__(self):
        return f'{self.party.code} ({self.get_role_display()})'


class CommercialProfile(BaseERPModel):
    party_role = models.OneToOneField(
        PartyRole,
        on_delete=models.CASCADE,
        related_name='commercial_profile',
    )
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_days = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Commercial - {self.party_role}'


class BankDetail(BaseERPModel):
    party_role = models.ForeignKey(
        PartyRole,
        on_delete=models.CASCADE,
        related_name='bank_details',
    )
    bank_name = models.CharField(max_length=150)
    branch_name = models.CharField(max_length=150, blank=True)
    account_no = models.CharField(max_length=30, db_index=True)
    ifsc_code = models.CharField(max_length=11, validators=[validate_ifsc])
    micr_no = models.CharField(max_length=15, blank=True)
    account_holder_name = models.CharField(max_length=150)

    class Meta:
        verbose_name_plural = 'Bank Details'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['party_role', 'account_no'],
                name='unique_bank_account_per_role',
            ),
        ]

    def __str__(self):
        return f'{self.bank_name} - {self.account_no[-4:]}'

    def clean(self):
        super().clean()
        if self.account_no and self.party_role_id:
            qs = BankDetail.objects.filter(
                party_role=self.party_role,
                account_no=self.account_no,
            ).exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    {'account_no': 'This account number already exists for this party role.'}
                )


class StatutoryDetail(BaseERPModel):
    party_role = models.OneToOneField(
        PartyRole,
        on_delete=models.CASCADE,
        related_name='statutory_detail',
    )
    cin_no = models.CharField('CIN No', max_length=21, blank=True)
    pan_no = models.CharField('PAN No', max_length=10, blank=True, validators=[validate_pan])
    tan_no = models.CharField('TAN No', max_length=10, blank=True)
    msme_no = models.CharField('MSME No', max_length=50, blank=True)
    esi_no = models.CharField('ESI No', max_length=50, blank=True)
    pf_no = models.CharField('PF No', max_length=50, blank=True)
    pan_card = models.FileField('PAN Card', upload_to='statutory/pan/', blank=True, null=True)
    msme_certificate = models.FileField('MSME Certificate', upload_to='statutory/msme/', blank=True, null=True)
    other_document = models.FileField('Other Document', upload_to='statutory/other/', blank=True, null=True)

    def __str__(self):
        return f'Statutory - {self.party_role}'


class ContactPerson(BaseERPModel):
    party_role = models.ForeignKey(
        PartyRole,
        on_delete=models.CASCADE,
        related_name='contacts',
    )
    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=100, blank=True)
    mobile_no = models.CharField(max_length=20, validators=[validate_mobile])
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PartyDocument(BaseERPModel):
    party_role = models.ForeignKey(
        PartyRole,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    document_type = models.CharField(max_length=30, choices=DocumentType.choices)
    file = models.FileField(upload_to='party_documents/%Y/%m/')
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_document_type_display()} - {self.party_role}'


class BrokerProfile(BaseERPModel):
    party_role = models.OneToOneField(
        PartyRole,
        on_delete=models.CASCADE,
        related_name='broker_profile',
    )
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    license_no = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f'Broker - {self.party_role}'


class CustomerProfile(BaseERPModel):
    party_role = models.OneToOneField(
        PartyRole,
        on_delete=models.CASCADE,
        related_name='customer_profile',
    )
    customer_segment = models.CharField(max_length=100, blank=True)
    billing_preference = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f'Customer - {self.party_role}'
