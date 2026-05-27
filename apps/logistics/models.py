from django.core.exceptions import ValidationError
from django.db import models

from apps.common.validators import validate_aadhar, validate_phone
from apps.core.models import BaseERPModel
from apps.transporters.models import TransporterProfile


class Truck(BaseERPModel):
    """Truck owner record: truck linked to a transporter."""

    transporter = models.ForeignKey(
        TransporterProfile,
        on_delete=models.CASCADE,
        related_name='trucks',
        verbose_name='Transporter',
    )
    truck_number = models.CharField('Truck Number', max_length=20, db_index=True)
    truck_owner = models.CharField('Truck Owner', max_length=150, blank=True)

    class Meta:
        ordering = ['truck_number']
        verbose_name = 'Truck'
        verbose_name_plural = 'Trucks'
        constraints = [
            models.UniqueConstraint(
                fields=['truck_number'],
                name='unique_truck_number',
            ),
        ]

    def __str__(self):
        return self.truck_number

    def clean(self):
        super().clean()
        if self.truck_number:
            normalized = self.truck_number.strip().upper()
            qs = Truck.objects.filter(truck_number__iexact=normalized).exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    {'truck_number': 'A truck with this number already exists.'}
                )
            self.truck_number = normalized


class TruckDriver(BaseERPModel):
    """Driver assigned to a truck (truck number & owner come from the truck)."""

    truck = models.ForeignKey(
        Truck,
        on_delete=models.CASCADE,
        related_name='drivers',
        verbose_name='Truck Number',
    )
    name = models.CharField('Name', max_length=150, blank=True)
    aadhar_number = models.CharField(
        'Aadhar Number', max_length=12, blank=True, validators=[validate_aadhar],
    )
    phone = models.CharField('Phone', max_length=20, blank=True, validators=[validate_phone])
    dl_number = models.CharField('DL Number', max_length=30, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Truck Driver'
        verbose_name_plural = 'Truck Drivers'

    def __str__(self):
        label = self.name or self.dl_number or self.phone or 'Driver'
        return f'{label} ({self.truck.truck_number})'

    @property
    def truck_number(self):
        return self.truck.truck_number

    @property
    def truck_owner_name(self):
        return self.truck.truck_owner
