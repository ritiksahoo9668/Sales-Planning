from rest_framework import serializers

from apps.logistics.models import Truck, TruckDriver
from apps.parties.models import (
    BankDetail,
    CommercialProfile,
    ContactPerson,
    Party,
    PartyDocument,
    PartyRole,
    StatutoryDetail,
)
from apps.transporters.models import TransporterProfile
from apps.vendors.models import VendorProfile


class BankDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetail
        fields = [
            'id', 'bank_name', 'branch_name', 'account_no',
            'ifsc_code', 'micr_no', 'account_holder_name', 'is_active',
        ]
        read_only_fields = ['id']


class ContactPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPerson
        fields = ['id', 'name', 'designation', 'mobile_no', 'email', 'is_active']
        read_only_fields = ['id']


class PartyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartyDocument
        fields = ['id', 'document_type', 'file', 'remarks', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class CommercialProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommercialProfile
        fields = ['id', 'credit_limit', 'credit_days']
        read_only_fields = ['id']


class StatutoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatutoryDetail
        fields = [
            'id', 'cin_no', 'pan_no', 'tan_no', 'msme_no',
            'esi_no', 'pf_no', 'pan_card', 'msme_certificate', 'other_document',
        ]
        read_only_fields = ['id']


class VendorProfileSerializer(serializers.ModelSerializer):
    vendor_type_name = serializers.CharField(
        source='vendor_type.name', read_only=True, allow_null=True
    )
    vendor_category_name = serializers.CharField(
        source='vendor_category.name', read_only=True, allow_null=True
    )
    vendor_sub_category_name = serializers.CharField(
        source='vendor_sub_category.name', read_only=True, allow_null=True
    )
    office_status_display = serializers.CharField(
        source='get_office_status_display', read_only=True
    )

    class Meta:
        model = VendorProfile
        fields = [
            'id', 'company_name',
            'vendor_type', 'vendor_type_name',
            'vendor_category', 'vendor_category_name',
            'vendor_sub_category', 'vendor_sub_category_name',
            'office_status', 'office_status_display',
            'gst_no', 'dispatch_location',
        ]
        read_only_fields = ['id']


class TruckDriverSerializer(serializers.ModelSerializer):
    truck_number = serializers.CharField(source='truck.truck_number', read_only=True)
    truck_owner = serializers.CharField(source='truck.truck_owner', read_only=True)
    transporter_name = serializers.CharField(
        source='truck.transporter.party_role.party.name',
        read_only=True,
    )

    class Meta:
        model = TruckDriver
        fields = [
            'id', 'truck', 'truck_number', 'truck_owner', 'transporter_name',
            'name', 'aadhar_number', 'phone', 'dl_number', 'is_active',
        ]
        read_only_fields = ['id', 'truck_number', 'truck_owner', 'transporter_name']


class TruckSerializer(serializers.ModelSerializer):
    drivers = TruckDriverSerializer(many=True, read_only=True)
    transporter_id = serializers.IntegerField(source='transporter_id', read_only=True)
    transporter_name = serializers.CharField(
        source='transporter.party_role.party.name',
        read_only=True,
    )

    class Meta:
        model = Truck
        fields = [
            'id', 'transporter', 'transporter_id', 'transporter_name',
            'truck_number', 'truck_owner', 'is_active', 'drivers',
        ]
        read_only_fields = ['id', 'transporter_id', 'transporter_name']

    def validate_truck_number(self, value):
        value = value.strip().upper()
        qs = Truck.objects.filter(truck_number__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('A truck with this number already exists.')
        return value


class TransporterProfileSerializer(serializers.ModelSerializer):
    trucks = TruckSerializer(many=True, read_only=True)
    market_state_name = serializers.CharField(
        source='market_state.name', read_only=True, allow_null=True
    )

    class Meta:
        model = TransporterProfile
        fields = [
            'id', 'market_state', 'market_state_name',
            'truck_owned_by', 'trucks',
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'truck_owned_by': {'label': 'Truck Owned By'},
            'market_state': {'label': 'Market / State'},
        }


class PartyRoleSerializer(serializers.ModelSerializer):
    commercial_profile = CommercialProfileSerializer(read_only=True)
    statutory_detail = StatutoryDetailSerializer(read_only=True)
    bank_details = BankDetailSerializer(many=True, read_only=True)
    contacts = ContactPersonSerializer(many=True, read_only=True)
    documents = PartyDocumentSerializer(many=True, read_only=True)
    vendor_profile = VendorProfileSerializer(read_only=True)
    transporter_profile = TransporterProfileSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = PartyRole
        fields = [
            'id', 'role', 'role_display', 'is_active',
            'commercial_profile', 'statutory_detail', 'bank_details',
            'contacts', 'documents', 'vendor_profile', 'transporter_profile',
        ]
        read_only_fields = ['id']


class PartySerializer(serializers.ModelSerializer):
    roles = PartyRoleSerializer(many=True, read_only=True)
    role_codes = serializers.ListField(
        child=serializers.ChoiceField(choices=PartyRole._meta.get_field('role').choices),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Party
        fields = [
            'id', 'code', 'name', 'email', 'phone', 'mobile_no',
            'address', 'location', 'is_active', 'roles', 'role_codes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']

    def create(self, validated_data):
        from apps.common.services import PartyCodeService
        role_codes = validated_data.pop('role_codes', [])
        validated_data['code'] = PartyCodeService.generate_code()
        party = Party.objects.create(**validated_data)
        for role in role_codes:
            PartyRole.objects.create(party=party, role=role)
        return party

    def update(self, instance, validated_data):
        role_codes = validated_data.pop('role_codes', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if role_codes is not None:
            existing = {r.role: r for r in instance.roles.all()}
            for role in role_codes:
                if role not in existing:
                    PartyRole.objects.create(party=instance, role=role)
                else:
                    obj = existing[role]
                    if not obj.is_active:
                        obj.is_active = True
                        obj.save(update_fields=['is_active', 'updated_at'])
            for role, obj in existing.items():
                if role not in role_codes and obj.is_active:
                    obj.is_active = False
                    obj.save(update_fields=['is_active', 'updated_at'])
        return instance


class VendorDetailSerializer(VendorProfileSerializer):
    party = PartySerializer(source='party_role.party', read_only=True)
    party_role_id = serializers.IntegerField(source='party_role.id', read_only=True)

    class Meta(VendorProfileSerializer.Meta):
        fields = VendorProfileSerializer.Meta.fields + ['party', 'party_role_id']


class TransporterDetailSerializer(TransporterProfileSerializer):
    party = PartySerializer(source='party_role.party', read_only=True)
    party_role_id = serializers.IntegerField(source='party_role.id', read_only=True)

    class Meta(TransporterProfileSerializer.Meta):
        fields = TransporterProfileSerializer.Meta.fields + ['party', 'party_role_id']
