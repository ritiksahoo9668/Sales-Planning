from django.urls import path

from . import views

app_name = 'parties'

urlpatterns = [
    path('', views.PartyListView.as_view(), name='party_list'),
    path('create/', views.PartyCreateView.as_view(), name='party_create'),
    path('<int:pk>/', views.PartyDetailView.as_view(), name='party_detail'),
    path('<int:pk>/edit/', views.PartyUpdateView.as_view(), name='party_edit'),
    path('<int:pk>/roles/<int:role_pk>/manage/', views.PartyRoleManageView.as_view(), name='party_role_manage'),
    path('<int:pk>/delete/', views.PartySoftDeleteView.as_view(), name='party_delete'),
]
