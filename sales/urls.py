from django.urls import path
from .views import SaleCreateView , SaleListView ,SaleInvoiceView

urlpatterns = [
    
    path('',SaleListView.as_view(),name= 'sale-list'),
    path('add/',SaleCreateView.as_view(),name='sale-add'),
    path('sale/<int:pk>/invoice/', SaleInvoiceView.as_view(), name='sale-invoice')
    
    
]
