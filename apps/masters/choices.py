from django.db import models


class PartyRoleType(models.TextChoices):
    VENDOR = 'vendor', 'Vendor'
    CUSTOMER = 'customer', 'Customer'
    BROKER = 'broker', 'Broker'
    TRANSPORTER = 'transporter', 'Transporter'
    MANUFACTURER = 'manufacturer', 'Manufacturer'


class OfficeStatus(models.TextChoices):
    """Static office status — not stored as a master table."""
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'


class PartyStatusFilter(models.TextChoices):
    """List-page filter for business partner active/inactive status."""
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'


class DocumentType(models.TextChoices):
    GST_CERTIFICATE = 'gst_certificate', 'GST Certificate'
    PAN_CARD = 'pan_card', 'PAN Card'
    CANCELLED_CHEQUE = 'cancelled_cheque', 'Cancelled Cheque'
    AGREEMENT = 'agreement', 'Agreement'
    MSME = 'msme', 'MSME Certificate'
    OTHER = 'other', 'Other'


class TruckOwnership(models.TextChoices):
    OWN = 'own', 'Own'
    MARKET = 'market', 'Market'
    ATTACHED = 'attached', 'Attached'
