from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import CreateView , UpdateView ,DeleteView#View جاهز من Django لإنشاء كائن جديد
from django.urls import reverse_lazy
from . models import Products

class Productlistview(ListView):
    model = Products
    template_name ='products/productlist.html'
    context_object_name = 'products'
class ProductCreateView(CreateView):
    model = Products
    fields = ['name','description','price','quantity','image'] #الحقول اللي المستخدم هيملأها في الفورم
    template_name = 'products/product_form.html' #قالب HTML للعرض
    success_url = reverse_lazy('product-list') #بعد الحفظ، يروح فين؟ هنا بيرجع لقائمة المنتجات
    #الاسم اللى هنا لازم يكون هو هو اللي فى url name 
class ProductUpdateView(UpdateView):
    model = Products
    fields = ['name','description', 'price','quantity']
    template_name = 'products/product_form.html' #ستخدم نفس القالب product_form.html لأن Django بيتعامل مع الفورم بنفس الطريقة سواء إضافة أو تعديل.
    success_url = reverse_lazy('product-list')
class ProductDeleteView(DeleteView):
    model = Products
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product-list')