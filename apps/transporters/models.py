from django.db import models

from apps.core.models import BaseERPModel
from apps.masters.choices import TruckOwnership
from apps.masters.models import MarketState
from apps.parties.models import PartyRole


class TransporterProfile(BaseERPModel):
    party_role = models.OneToOneField(
        PartyRole,
        on_delete=models.CASCADE,
        related_name='transporter_profile',
    )
    market_state = models.ForeignKey(
        MarketState,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transporters',
        verbose_name='Market / State',
    )
    truck_owned_by = models.CharField(
        'Truck Owned By',
        max_length=20,
        choices=TruckOwnership.choices,
        default=TruckOwnership.OWN,
    )

    class Meta:
        verbose_name = 'Transporter Profile'
        verbose_name_plural = 'Transporter Profiles'

    def __str__(self):
        return f'Transporter - {self.party_role}'
