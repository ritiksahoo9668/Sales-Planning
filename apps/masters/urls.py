from django.urls import path

from . import views

app_name = 'masters'

urlpatterns = [
    path('vendor-type/create/', views.vendor_type_create, name='vendor_type_create'),
    path('vendor-type/delete/', views.vendor_type_delete, name='vendor_type_delete'),
    path('vendor-category/create/', views.vendor_category_create, name='vendor_category_create'),
    path('vendor-category/delete/', views.vendor_category_delete, name='vendor_category_delete'),
    path('vendor-sub-category/create/', views.vendor_sub_category_create, name='vendor_sub_category_create'),
    path('vendor-sub-category/delete/', views.vendor_sub_category_delete, name='vendor_sub_category_delete'),
    path('vendor-sub-categories/', views.vendor_sub_categories_list, name='vendor_sub_categories_list'),
]
