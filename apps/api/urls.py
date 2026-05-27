from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .viewsets import (
    PartyViewSet,
    TransporterViewSet,
    TruckDriverViewSet,
    TruckViewSet,
    VendorViewSet,
)

router = DefaultRouter()
router.register('parties', PartyViewSet, basename='party')
router.register('vendors', VendorViewSet, basename='vendor')
router.register('transporters', TransporterViewSet, basename='transporter')
router.register('trucks', TruckViewSet, basename='truck')
router.register('drivers', TruckDriverViewSet, basename='driver')

urlpatterns = [
    path('', include(router.urls)),
]
