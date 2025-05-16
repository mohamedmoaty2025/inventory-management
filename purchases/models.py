from django.db import models
from products.models import Products



#بيانات المورد

class Supplier(models.Model):
    name = models.CharField(max_length= 100 ,verbose_name='اسم المورد')
    phone = models.CharField(max_length=50 , null = True ,blank=True ,verbose_name= 'رقم الهاتف')
    address = models.TextField(null=True,blank=True ,verbose_name='العنوان')
    
    def __str__(self):
        return self.name
    
    
class Purchase(models.Model):
    product_new = models.CharField(max_length=100,null= True,blank=True,verbose_name='منتج جديد')
    product = models.ForeignKey(Products , on_delete=models.CASCADE ,verbose_name='المنتج', null= True ,blank= True) 
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True,verbose_name='تاريخ الشراء')
    supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE ,verbose_name= 'المورد')
    # image = models.ImageField(upload_to='static/images',null=True, blank=True)
    
    def __str__(self):
        return f"شراء {self.quantity} من {self.product} -{self.supplier}"

