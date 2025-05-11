from django.db import models
from products.models import Products #استعاء الموديلز من تطبيقه  products
from django.utils import timezone

class Sale(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE) #المنتج المباع
    quantity = models.PositiveIntegerField()#كمية المنتج المباع
    sale_date = models.DateTimeField(default=timezone.now) #تاريخ البيع
    customer_name = models.CharField(max_length=100)
    discount = models.DecimalField(max_digits=10 , decimal_places=2 ,default=0)
    tax = models.DecimalField(max_digits=10 , decimal_places=2 ,default=0)
    
    def __str__(self):
        return f'{self.product.name} - {self.quantity} وحدة'
    @property #دي decorator بتخلي الـ function اللي بعدها تشتغل كأنها "خاصية" (property)
    def total_price(self):
        return self.product.price * self.quantity
    
    
    # return self.product.price * self.quantity
# self.product: بيرجع كائن المنتج المرتبط بالبيع.
# self.product.price: سعر الوحدة الواحدة من المنتج.
# self.quantity: عدد الوحدات اللي اتباعت.
# ⏱️ مثال عملي: لو بيعنا 3 وحدات من منتج سعره 50 جنيه:
# product.price = 50
# quantity = 3
# total_price = 50 × 3 = 150
 # داله بتحسب السعر بعد الخصم والضريبة المضافة
    def total_price(self):
        base = self.product.price*self.quantity
        total = base - self.discount
        total +=(total*self.tax/100)
        return total


