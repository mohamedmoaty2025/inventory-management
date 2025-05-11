from django.urls import path
from .views import SupplierCreateView, SupplierListView

urlpatterns = [
    path('add/', SupplierCreateView.as_view(), name='supplier-add'),
    path('list/', SupplierListView.as_view(), name='supplier-list'),
]
