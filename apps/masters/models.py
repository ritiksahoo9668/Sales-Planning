from django.db import models

from apps.core.models import BaseERPModel


class VendorType(BaseERPModel):
    """Master: vendor type (Registered, Unregistered, etc.)."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Vendor Type'
        verbose_name_plural = 'Vendor Types'
        ordering = ['name']

    def __str__(self):
        return self.name


class VendorCategory(BaseERPModel):
    """Master: vendor category."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Vendor Category'
        verbose_name_plural = 'Vendor Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class VendorSubCategory(BaseERPModel):
    """Master: vendor sub-category linked to a category."""
    category = models.ForeignKey(
        VendorCategory,
        on_delete=models.PROTECT,
        related_name='subcategories',
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Vendor Sub Categories'
        ordering = ['category', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'name'],
                name='unique_vendor_subcategory_per_category',
            ),
        ]

    def __str__(self):
        return f'{self.category.name} - {self.name}'


class MarketState(BaseERPModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
