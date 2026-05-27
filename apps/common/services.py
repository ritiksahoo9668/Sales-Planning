"""Service layer for party-related business operations."""
from django.db import transaction

from apps.parties.models import Party, PartyRole


class PartyCodeService:
    """Generate sequential party codes."""

    PREFIX = 'PTY'

    @classmethod
    def generate_code(cls):
        last = Party.objects.order_by('-id').values_list('code', flat=True).first()
        if last and last.startswith(cls.PREFIX):
            try:
                num = int(last.replace(cls.PREFIX, '')) + 1
            except ValueError:
                num = 1
        else:
            num = Party.objects.count() + 1
        return f'{cls.PREFIX}{num:06d}'


class PartyRoleService:
    @staticmethod
    @transaction.atomic
    def activate_role(party_role):
        party_role.is_active = True
        party_role.save(update_fields=['is_active', 'updated_at'])
        return party_role

    @staticmethod
    @transaction.atomic
    def deactivate_role(party_role):
        party_role.is_active = False
        party_role.save(update_fields=['is_active', 'updated_at'])
        return party_role
