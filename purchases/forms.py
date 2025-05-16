# from django import forms
# from .models import Purchase



# class PurchaseForm(forms.ModelForm):
#     product_name = forms.CharField(label='اسم المنتج', max_length= 100)
    
#     class Meta:
#         model = Purchase
#         fields = ['product_name','price','quantity']
from django import forms
from .models import Purchase ,Supplier 
from products.models import Category

class PurchaseForm(forms.ModelForm):
    image = forms.ImageField(required=False, label="صورة المنتج")
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="فئة المنتج (عند إدخال منتج جديد فقط)"
    )
    class Meta:
        model = Purchase
        fields = ['product_new', 'product', 'category' ,'price', 'quantity', 'supplier']
        labels = {
            'product_new': 'منتج جديد (اتركه فارغًا إن كنت ستختار منتج موجود)',
            'product': 'المنتج (اختر من القائمة أو أدخل منتجًا جديدًا)',
            'category': 'فئة المنتج',
            'price': 'السعر',
            'quantity': 'الكمية',
            'supplier': 'اسم المورد',
        }

    def clean(self):
        cleaned_data = super().clean()
        product_new = cleaned_data.get("product_new")
        product = cleaned_data.get("product")
        category = cleaned_data.get("category")

        if not product_new and not product:
            raise forms.ValidationError("يجب إدخال اسم منتج جديد أو اختيار منتج من القائمة.")
        if product_new and product:
            raise forms.ValidationError("يرجى إدخال اسم منتج جديد أو اختيار منتج، وليس كليهما.")
        if product_new and not category:
            raise forms.ValidationError("عند إدخال منتج جديد يجب اختيار فئة له.")
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name','phone','address']
        labels ={
        'name':'اسم المورد',
        'phone':'رقم الهاتف',
        'address':'العنوان'
        }