from django.shortcuts import render
from products.models import Products
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from .models import Purchase ,Supplier
from .forms import PurchaseForm ,SupplierForm
from django.contrib import messages

class PurchaseCreateView(CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'purchases/purchase_form.html'
    success_url = reverse_lazy('purchase-add')

    def form_valid(self, form):
        product_name = form.cleaned_data['product']
        quantity = form.cleaned_data['quantity']
        price = form.cleaned_data['price']
        supplier = form.cleaned_data['supplier']

    # ابحث عن المنتج بدون إنشاءه
        try:
            product = Products.objects.get(name=product_name)
            product.price = price  # تحدّث السعر
            product.quantity += quantity  # زوّد الكمية
        except Products.DoesNotExist:
        # المنتج جديد → أنشئه بالسعر والكمية
            product = Products(name=product_name, price=price, quantity=quantity)

        product.save()

        purchase = form.save(commit=False)
        purchase.product = product.name
        purchase.supplier = supplier
        purchase.save()

        messages.success(self.request, "تم حفظ عملية الشراء بنجاح.")
        return super().form_valid(form)

class SupplierCreateView(CreateView):
    model = Supplier 
    form_class = SupplierForm
    template_name = 'purchases/supplier_form.html'
    success_url = reverse_lazy('supplier-list')
    
class SupplierListView(ListView):
    model = Supplier
    template_name = 'purchases/supplier_list.html'
    context_object_name = 'suppliers'
    
     
