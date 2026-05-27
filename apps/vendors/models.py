from django.db import models

from apps.common.validators import validate_gst
from apps.core.models import BaseERPModel
from apps.masters.choices import OfficeStatus
from apps.masters.models import VendorCategory, VendorSubCategory, VendorType
from apps.parties.models import PartyRole


class VendorProfile(BaseERPModel):
    party_role = models.OneToOneField(
        PartyRole,
        on_delete=models.CASCADE,
        related_name='vendor_profile',
    )
    company_name = models.CharField(max_length=255)
    vendor_type = models.ForeignKey(
        VendorType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='vendors',
    )
    vendor_category = models.ForeignKey(
        VendorCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendors',
    )
    vendor_sub_category = models.ForeignKey(
        VendorSubCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendors',
    )
    office_status = models.CharField(
        'Office Status',
        max_length=20,
        choices=OfficeStatus.choices,
        default=OfficeStatus.ACTIVE,
    )
    gst_no = models.CharField('GST No', max_length=15, blank=True, validators=[validate_gst])
    dispatch_location = models.CharField(max_length=255, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['company_name']),
            models.Index(fields=['gst_no']),
            models.Index(fields=['vendor_type', 'office_status']),
        ]

    def __str__(self):
        return self.company_name or str(self.party_role)
