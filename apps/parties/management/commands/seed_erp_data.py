"""Seed sample ERP master data for development and demos."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.logistics.models import Truck, TruckDriver
from apps.masters.choices import OfficeStatus, PartyRoleType, TruckOwnership
from apps.masters.models import MarketState, VendorCategory, VendorSubCategory, VendorType
from apps.parties.models import (
    BankDetail,
    CommercialProfile,
    ContactPerson,
    Party,
    PartyRole,
    StatutoryDetail,
)
from apps.transporters.models import TransporterProfile
from apps.vendors.models import VendorProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Load sample business partner master data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-admin-password',
            action='store_true',
            help='Reset admin user password to admin123 (dev only)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True},
        )
        if options['reset_admin_password'] or not admin.has_usable_password():
            admin.set_password('admin123')
            admin.save()

        vendor_type, _ = VendorType.objects.get_or_create(
            code='registered',
            defaults={'name': 'Registered', 'description': 'GST registered vendor'},
        )
        category, _ = VendorCategory.objects.get_or_create(name='Raw Material')
        sub_category, _ = VendorSubCategory.objects.get_or_create(
            category=category, name='Steel',
        )
        market_state, _ = MarketState.objects.get_or_create(
            name='Maharashtra', defaults={'code': 'MH'},
        )

        party, created = Party.objects.get_or_create(
            code='PTY000001',
            defaults={
                'name': 'Shree Logistics & Supplies Pvt Ltd',
                'email': 'contact@shreelogistics.in',
                'phone': '9876543210',
                'mobile_no': '9876543210',
                'address': 'Plot 12, MIDC Industrial Area',
                'location': 'Pune, Maharashtra',
                'created_by': admin,
            },
        )

        vendor_role, _ = PartyRole.objects.get_or_create(
            party=party, role=PartyRoleType.VENDOR,
            defaults={'created_by': admin},
        )
        transporter_role, _ = PartyRole.objects.get_or_create(
            party=party, role=PartyRoleType.TRANSPORTER,
            defaults={'created_by': admin},
        )
        customer_role, _ = PartyRole.objects.get_or_create(
            party=party,
            role=PartyRoleType.CUSTOMER,
            defaults={'created_by': admin},
        )

        VendorProfile.objects.get_or_create(
            party_role=vendor_role,
            defaults={
                'company_name': 'Shree Logistics & Supplies Pvt Ltd',
                'vendor_category': category,
                'vendor_sub_category': sub_category,
                'vendor_type': vendor_type,
                'office_status': OfficeStatus.ACTIVE,
                'gst_no': '27AABCS1429B1Z5',
                'dispatch_location': 'Pune Warehouse',
                'created_by': admin,
            },
        )

        CommercialProfile.objects.get_or_create(
            party_role=vendor_role,
            defaults={'credit_limit': Decimal('500000.00'), 'credit_days': 30},
        )
        StatutoryDetail.objects.get_or_create(
            party_role=vendor_role,
            defaults={'pan_no': 'AABCS1429B', 'msme_no': 'UDYAM-MH-12-0012345'},
        )
        BankDetail.objects.get_or_create(
            party_role=vendor_role,
            account_no='123456789012',
            defaults={
                'bank_name': 'State Bank of India',
                'branch_name': 'Pune Camp',
                'ifsc_code': 'SBIN0001234',
                'account_holder_name': 'Shree Logistics & Supplies Pvt Ltd',
                'created_by': admin,
            },
        )
        ContactPerson.objects.get_or_create(
            party_role=vendor_role,
            name='Rajesh Kumar',
            defaults={
                'designation': 'Purchase Manager',
                'mobile_no': '9123456780',
                'email': 'rajesh@shreelogistics.in',
                'created_by': admin,
            },
        )

        transporter, _ = TransporterProfile.objects.get_or_create(
            party_role=transporter_role,
            defaults={
                'market_state': market_state,
                'truck_owned_by': TruckOwnership.OWN,
                'created_by': admin,
            },
        )
        truck, _ = Truck.objects.get_or_create(
            transporter=transporter,
            truck_number='MH12AB1234',
            defaults={'truck_owner': 'Shree Logistics', 'created_by': admin},
        )
        TruckDriver.objects.get_or_create(
            truck=truck,
            dl_number='MH1220200012345',
            defaults={
                'name': 'Suresh Patil',
                'aadhar_number': '234567890123',
                'phone': '9988776655',
                'created_by': admin,
            },
        )

        CommercialProfile.objects.get_or_create(
            party_role=customer_role,
            defaults={'credit_limit': Decimal('250000.00'), 'credit_days': 15},
        )

        party2, _ = Party.objects.get_or_create(
            code='PTY000002',
            defaults={
                'name': 'Global Broker Associates',
                'email': 'info@globalbroker.in',
                'mobile_no': '9012345678',
                'location': 'Mumbai',
                'created_by': admin,
            },
        )
        PartyRole.objects.get_or_create(
            party=party2, role=PartyRoleType.BROKER, defaults={'created_by': admin},
        )

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete. Admin login: admin / admin123. '
            f'Sample party: {party.code} (created={created}).'
        ))
