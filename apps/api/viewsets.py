from django.db.models import Exists, OuterRef
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.logistics.models import Truck, TruckDriver
from apps.parties.models import Party, PartyRole
from apps.transporters.models import TransporterProfile
from apps.vendors.models import VendorProfile

from .serializers import (
    PartySerializer,
    TransporterDetailSerializer,
    TruckDriverSerializer,
    TruckSerializer,
    VendorDetailSerializer,
)


class PartyFilter(filters.FilterSet):
    role = filters.CharFilter(method='filter_role')
    is_active = filters.BooleanFilter()

    class Meta:
        model = Party
        fields = ['is_active', 'role', 'location']

    def filter_role(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Exists(
                PartyRole.objects.filter(
                    party_id=OuterRef('pk'),
                    role=value,
                    is_active=True,
                    is_deleted=False,
                )
            )
        )


class PartyViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.filter(is_deleted=False).prefetch_related(
        'roles__bank_details',
        'roles__contacts',
        'roles__documents',
        'roles__commercial_profile',
        'roles__statutory_detail',
        'roles__vendor_profile',
        'roles__transporter_profile__trucks__drivers',
    )
    serializer_class = PartySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PartyFilter
    search_fields = ['code', 'name', 'email', 'mobile_no', 'phone']
    ordering_fields = ['created_at', 'name', 'code']
    ordering = ['-created_at']


class VendorViewSet(viewsets.ModelViewSet):
    queryset = VendorProfile.objects.select_related(
        'party_role__party',
        'vendor_type',
        'vendor_category',
        'vendor_sub_category',
    ).filter(is_deleted=False)
    serializer_class = VendorDetailSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['vendor_type', 'office_status', 'vendor_category', 'is_active']
    search_fields = [
        'company_name', 'gst_no',
        'party_role__party__name', 'party_role__party__code',
    ]
    ordering_fields = ['company_name', 'created_at']
    ordering = ['company_name']


class TransporterViewSet(viewsets.ModelViewSet):
    queryset = TransporterProfile.objects.select_related(
        'party_role__party', 'market_state'
    ).prefetch_related('trucks__drivers').filter(is_deleted=False)
    serializer_class = TransporterDetailSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['truck_owned_by', 'market_state', 'is_active']
    search_fields = ['party_role__party__name', 'party_role__party__code']
    ordering = ['party_role__party__name']


class TruckFilter(filters.FilterSet):
    transporter = filters.NumberFilter(field_name='transporter_id')

    class Meta:
        model = Truck
        fields = ['transporter', 'is_active']


class TruckViewSet(viewsets.ModelViewSet):
    queryset = Truck.objects.select_related(
        'transporter__party_role__party'
    ).prefetch_related('drivers').filter(is_deleted=False)
    serializer_class = TruckSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TruckFilter
    search_fields = ['truck_number', 'owner_name', 'transporter__party_role__party__name']
    ordering_fields = ['truck_number', 'created_at']
    ordering = ['truck_number']


class TruckDriverViewSet(viewsets.ModelViewSet):
    queryset = TruckDriver.objects.select_related(
        'truck__transporter__party_role__party'
    ).filter(is_deleted=False)
    serializer_class = TruckDriverSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['truck', 'is_active']
    search_fields = ['name', 'phone', 'dl_number', 'aadhar_number', 'truck__truck_number']
    ordering = ['name']
