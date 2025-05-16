from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Products  # غير اسم الموديل حسب مشروعك
from sales.models import Sale  # نفس الفكرة
from purchases.models import Purchase  # نفس الفكرة

class Home(LoginRequiredMixin,TemplateView):
    template_name = 'Home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products_count'] = Products.objects.count()
        context['sales_count'] = Sale.objects.count()
        context['purchases_count'] = Purchase.objects.count()
        context['low_stock'] = Products.objects.filter(quantity__lt=5)
        context['out_of_stock'] = Products.objects.filter(quantity=0)# المنتجات القليلة
        return context