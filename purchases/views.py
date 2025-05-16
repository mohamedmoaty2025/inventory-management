from django.shortcuts import render , redirect
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

    # def form_valid(self, form):
    #     product_new =form.cleaned_data['product_new']
    #     product = form.clean_data['product']
    #     quantity = form.cleaned_data['quantity']
    #     price = form.cleaned_data['price']
    #     supplier = form.cleaned_data['supplier']

    # # ابحث عن المنتج بدون إنشاءه
    #     try:
    #         product = Products.objects.get(name=product_new)
    #         product.price = price  # تحدّث السعر
    #         product.quantity += quantity  # زوّد الكمية
    #     except Products.DoesNotExist:
    #     # المنتج جديد → أنشئه بالسعر والكمية
    #         product = Products(name=product_new, price=price, quantity=quantity)

    #     product.save()

    #     purchase = form.save(commit=False)
    #     purchase.product = product.name
    #     purchase.supplier = supplier
    #     purchase.save()

    #     messages.success(self.request, "تم حفظ عملية الشراء بنجاح.")
    #     return super().form_valid(form)
    def form_valid(self, form):
        product_new = form.cleaned_data['product_new']
        product = form.cleaned_data['product']
        category = form.cleaned_data['category']
        quantity = form.cleaned_data['quantity']
        price = form.cleaned_data['price']
        supplier = form.cleaned_data['supplier']
        image = self.request.FILES.get('image')
        

    # إذا تم اختيار منتج جديد بدل الموجود
        if product_new:
            try:
                product = Products.objects.get(name=product_new)
                product.price = price
                product.quantity += quantity
                if image:
                    product.image = image
                if category:
                    product.category = category
            except Products.DoesNotExist:
                product = Products(name=product_new, price=price, quantity=quantity,category=category)
                if image:
                    product.image = image
                product.save()

    # إذا تم اختيار منتج موجود من القائمة
        elif product:
            product.price = price
            product.quantity += quantity
            product.save()

        else:
            messages.error(self.request, "يجب تحديد منتج أو إدخال اسم منتج جديد.")
            return self.form_invalid(form)

        purchase = form.save(commit=False)
        purchase.product = product
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
    
def add_supplier(requst):
    if requst.method == 'POST':
        form = SupplierForm(requst.POST)
        if form.is_valid():
            form.save()
            return redirect("supplier-list")
    else :
        form = SupplierForm()
        return render(requst, 'purchases/supplier_form.html', {'form': form})
