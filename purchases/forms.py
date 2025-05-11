# from django import forms
# from .models import Purchase



# class PurchaseForm(forms.ModelForm):
#     product_name = forms.CharField(label='اسم المنتج', max_length= 100)
    
#     class Meta:
#         model = Purchase
#         fields = ['product_name','price','quantity']
from django import forms
from .models import Purchase ,Supplier

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['product', 'price', 'quantity','supplier']
        labels = {
            'product': 'اسم المنتج',
            'price': 'السعر',
            'quantity': 'الكمية',
            'supplier':'اسم المورد'
        }
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name','phone','address']
        labels ={
        'name':'اسم المورد',
        'phone':'رقم الهاتف',
        'address':'العنوان'
        }