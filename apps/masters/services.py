"""Create vendor master records from the portal."""
from django.utils.text import slugify

from apps.masters.models import VendorCategory, VendorSubCategory, VendorType


def _unique_type_code(name: str) -> str:
    base = slugify(name).replace('-', '_')[:45] or 'vendor_type'
    code = base
    n = 1
    while VendorType.objects.filter(code=code).exists():
        code = f'{base}_{n}'[:50]
        n += 1
    return code


def create_vendor_type(name: str, user=None) -> VendorType:
    name = name.strip()
    if not name:
        raise ValueError('Name is required.')
    existing = VendorType.objects.filter(
        name__iexact=name, is_deleted=False,
    ).first()
    if existing:
        return existing
    return VendorType.objects.create(
        name=name,
        code=_unique_type_code(name),
        created_by=user if user and user.is_authenticated else None,
    )


def create_vendor_category(name: str, user=None) -> VendorCategory:
    name = name.strip()
    if not name:
        raise ValueError('Name is required.')
    existing = VendorCategory.objects.filter(
        name__iexact=name, is_deleted=False,
    ).first()
    if existing:
        return existing
    return VendorCategory.objects.create(
        name=name,
        created_by=user if user and user.is_authenticated else None,
    )


def create_vendor_sub_category(category_id: int, name: str, user=None) -> VendorSubCategory:
    name = name.strip()
    if not name:
        raise ValueError('Name is required.')
    if not category_id:
        raise ValueError('Select a vendor category first.')
    category = VendorCategory.objects.filter(
        pk=category_id, is_active=True, is_deleted=False,
    ).first()
    if not category:
        raise ValueError('Invalid vendor category.')
    existing = VendorSubCategory.objects.filter(
        category=category, name__iexact=name, is_deleted=False,
    ).first()
    if existing:
        return existing
    return VendorSubCategory.objects.create(
        category=category,
        name=name,
        created_by=user if user and user.is_authenticated else None,
    )


def delete_vendor_type(type_id: int):
    obj = VendorType.objects.filter(pk=type_id, is_deleted=False).first()
    if not obj:
        raise ValueError('Vendor type not found.')
    obj.soft_delete()


def delete_vendor_category(category_id: int):
    obj = VendorCategory.objects.filter(pk=category_id, is_deleted=False).first()
    if not obj:
        raise ValueError('Vendor category not found.')
    VendorSubCategory.objects.filter(category=obj, is_deleted=False).update(
        is_active=False,
        is_deleted=True,
    )
    obj.soft_delete()


def delete_vendor_sub_category(sub_category_id: int):
    obj = VendorSubCategory.objects.filter(pk=sub_category_id, is_deleted=False).first()
    if not obj:
        raise ValueError('Vendor sub category not found.')
    obj.soft_delete()
