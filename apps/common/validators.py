"""
Reusable field validators for Indian statutory and banking formats.
"""
import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

GSTIN_REGEX = re.compile(
    r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
)
PAN_REGEX = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
IFSC_REGEX = re.compile(r'^[A-Z]{4}0[A-Z0-9]{6}$')
PHONE_REGEX = re.compile(r'^[6-9]\d{9}$')
AADHAR_REGEX = re.compile(r'^\d{12}$')


def validate_gst(value):
    if not value:
        return
    gst = value.strip().upper()
    if not GSTIN_REGEX.match(gst):
        raise ValidationError(
            _('Invalid GST number. Expected format: 22AAAAA0000A1Z5'),
            code='invalid_gst',
        )


def validate_pan(value):
    if not value:
        return
    pan = value.strip().upper()
    if not PAN_REGEX.match(pan):
        raise ValidationError(
            _('Invalid PAN number. Expected format: ABCDE1234F'),
            code='invalid_pan',
        )


def validate_ifsc(value):
    if not value:
        return
    ifsc = value.strip().upper()
    if not IFSC_REGEX.match(ifsc):
        raise ValidationError(
            _('Invalid IFSC code. Expected format: SBIN0001234'),
            code='invalid_ifsc',
        )


def normalize_indian_mobile(value):
    """
  Normalize Indian mobile to 10 digits.
  Accepts: 9668123855, +91 9668123855, 919668123855, 91-9668123855
    """
    if not value:
        return ''
    digits = re.sub(r'\D', '', str(value).strip())
    if len(digits) == 12 and digits.startswith('91'):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith('0'):
        digits = digits[1:]
    return digits


def _normalize_indian_digits(value):
    return normalize_indian_mobile(value)


def validate_mobile(value):
    """Indian mobile: 10 digits, optional +91 prefix."""
    if not value:
        return
    digits = normalize_indian_mobile(value)
    if len(digits) != 10 or not PHONE_REGEX.match(digits):
        raise ValidationError(
            _('Enter a valid mobile number (e.g. 9668123855 or +91 9668123855).'),
            code='invalid_mobile',
        )


def validate_phone(value):
    """Alias for mobile validation (contacts, drivers)."""
    validate_mobile(value)


def validate_aadhar(value):
    if not value:
        return
    digits = re.sub(r'\D', '', value)
    if not AADHAR_REGEX.match(digits):
        raise ValidationError(
            _('Invalid Aadhar number. Must be 12 digits.'),
            code='invalid_aadhar',
        )
