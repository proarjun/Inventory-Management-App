from django.urls import path
from .views import inventory_list, per_product_view, add_product, delete_product, update_product, dashboard

urlpatterns = [
    path("", inventory_list, name= 'inventory_list'),
    path("per_product/<int:pk>", per_product_view, name= 'product_view'),
    path("add_inventory/", add_product, name= 'add_product'),
    path("update_inventory/<int:pk>", update_product, name= 'update_product'),
    path("delete/<int:pk>", delete_product, name= 'delete_product'),
    path("dashboard/", dashboard, name= 'dashboard'),
]