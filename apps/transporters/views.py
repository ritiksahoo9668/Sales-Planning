from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from apps.common.mixins import ERPLoginRequiredMixin
from apps.logistics.models import Truck
from apps.transporters.forms import TruckDriverFormSet, _driver_row_has_data


def _transport_manage_url(party_pk, role_pk, tab='transport'):
    url = reverse('parties:party_role_manage', kwargs={'pk': party_pk, 'role_pk': role_pk})
    return f'{url}?tab={tab}'


class TruckDriverManageView(ERPLoginRequiredMixin, View):
    template_name = 'transporters/truck_drivers.html'

    def get_truck(self, truck_pk):
        return get_object_or_404(
            Truck.objects.select_related(
                'transporter__party_role__party',
                'transporter__market_state',
            ).prefetch_related('drivers'),
            pk=truck_pk,
            is_deleted=False,
        )

    def get(self, request, truck_pk):
        truck = self.get_truck(truck_pk)
        party_role = truck.transporter.party_role
        formset = TruckDriverFormSet(instance=truck, prefix='driver')
        return render(request, self.template_name, {
            'truck': truck,
            'party': party_role.party,
            'party_role': party_role,
            'formset': formset,
            'back_url': _transport_manage_url(party_role.party_id, party_role.pk),
        })

    def post(self, request, truck_pk):
        truck = self.get_truck(truck_pk)
        party_role = truck.transporter.party_role
        formset = TruckDriverFormSet(request.POST, instance=truck, prefix='driver')

        if formset.is_valid():
            with transaction.atomic():
                user = request.user if request.user.is_authenticated else None
                drivers = formset.save(commit=False)
                for driver in drivers:
                    if not _driver_row_has_data({
                        'name': driver.name,
                        'aadhar_number': driver.aadhar_number,
                        'phone': driver.phone,
                        'dl_number': driver.dl_number,
                    }):
                        if driver.pk:
                            driver.delete()
                        continue
                    if user:
                        driver.updated_by = user
                    driver.save()
                for obj in formset.deleted_objects:
                    obj.delete()
            messages.success(request, 'Truck drivers saved.')
            return redirect(_transport_manage_url(party_role.party_id, party_role.pk))

        messages.error(request, 'Please correct the errors below.')
        return render(request, self.template_name, {
            'truck': truck,
            'party': party_role.party,
            'party_role': party_role,
            'formset': formset,
            'back_url': _transport_manage_url(party_role.party_id, party_role.pk),
        })
