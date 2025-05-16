from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum, F, ExpressionWrapper, DecimalField

from .models import Products, Category
from purchases.models import Purchase  # تأكد إن ده هو اسم التطبيق اللي فيه موديل Purchase

class Productlistview(ListView):
    model = Products
    template_name = 'products/productlist.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Products.objects.filter(name__icontains=query)
        return Products.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        today = timezone.localdate()
        current_month = today.month
        current_year = today.year

        # إجمالي مشتريات اليوم (الكمية * السعر)
        total_today = Purchase.objects.filter(
            purchase_date__date=today
        ).aggregate(
            total=Sum(ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField()))
        )['total'] or 0

        # إجمالي مشتريات الشهر
        total_month = Purchase.objects.filter(
            purchase_date__month=current_month,
            purchase_date__year=current_year
        ).aggregate(
            total=Sum(ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField()))
        )['total'] or 0

        # أكثر المنتجات شراءً من حيث الكمية
        top_purchased = Purchase.objects.values(
            'product__name'
        ).annotate(
            total_quantity=Sum('quantity')
        ).order_by('-total_quantity')[:5]  # أفضل 5 منتجات

        context['total_today'] = total_today
        context['total_month'] = total_month
        context['top_purchased'] = top_purchased

        return context


class ProductUpdateView(UpdateView):
    model = Products
    fields = ['name', 'description', 'price', 'quantity', 'image', 'category']
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product-list')


class ProductDeleteView(DeleteView):
    model = Products
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product-list')


class CategoryCreateView(CreateView):
    model = Category
    fields = ['name']
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('product-list')
