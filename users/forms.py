from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm ,AuthenticationForm

#نموذج تسجيل دخول المستخدمين الجدد 
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta :
        model = User
        fields = ['username','email','password1','password2']
        def clean_email(self):
            email = self.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("هذا البريد مسجل بالفعل.")
            return email
        
        
#نموذج تسجيل الدخول

class UserLoginForm(AuthenticationForm):
    username =forms.CharField(label= 'اسم المستخدم')
    password = forms.CharField(widget=forms.PasswordInput ,label='كلمة المرور')
    
class UserUpdateForm(forms.ModelForm):
    class Meta :
        model = User
        fields = ['username','email']
        labls = {
            'username':'اسم المستخدم',
            'email':'البريد الإلكترونى',
        }
            
        
    