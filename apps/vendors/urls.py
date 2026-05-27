from django.urls import path

from apps.parties.views import PartyRoleManageView

app_name = 'vendors'

urlpatterns = [
    path(
        'manage/<int:pk>/<int:role_pk>/',
        PartyRoleManageView.as_view(),
        name='vendor_manage',
    ),
]
