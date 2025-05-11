from django.urls import path
from .views import PurchaseCreateView ,SupplierCreateView ,SupplierListView

urlpatterns = [
    path('add/',PurchaseCreateView.as_view(),name='purchase-add'),
    
]
