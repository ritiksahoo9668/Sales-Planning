"""Seed vendor master data: types, categories, sub-categories."""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.masters.models import VendorCategory, VendorSubCategory, VendorType


class Command(BaseCommand):
    help = 'Load vendor type, category, and sub-category masters'

    @transaction.atomic
    def handle(self, *args, **options):
        types = [
            ('registered', 'Registered', 'GST registered vendor'),
            ('unregistered', 'Unregistered', 'Unregistered vendor'),
            ('composite', 'Composite', 'Composite dealer'),
        ]
        for code, name, desc in types:
            VendorType.objects.get_or_create(
                code=code,
                defaults={'name': name, 'description': desc},
            )

        categories = {
            'Raw Material': ['Steel', 'Cement', 'Chemicals'],
            'Services': ['Transport', 'Labour'],
            'Trading': ['Import', 'Domestic'],
        }
        for cat_name, subs in categories.items():
            category, _ = VendorCategory.objects.get_or_create(name=cat_name)
            for sub_name in subs:
                VendorSubCategory.objects.get_or_create(
                    category=category,
                    name=sub_name,
                )

        self.stdout.write(self.style.SUCCESS(
            f'Vendor masters ready: {VendorType.objects.count()} types, '
            f'{VendorCategory.objects.count()} categories, '
            f'{VendorSubCategory.objects.count()} sub-categories.'
        ))
