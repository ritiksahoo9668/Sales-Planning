from django.urls import path

from apps.parties.views import PartyRoleManageView

from . import views

app_name = 'transporters'

urlpatterns = [
    path(
        'manage/<int:pk>/<int:role_pk>/',
        PartyRoleManageView.as_view(),
        name='transporter_manage',
    ),
    path(
        'trucks/<int:truck_pk>/drivers/',
        views.TruckDriverManageView.as_view(),
        name='truck_drivers',
    ),
]
