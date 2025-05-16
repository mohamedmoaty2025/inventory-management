from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

# تسجيل مستخدم جديد
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # حفظ المستخدم الجديد
            messages.success(request, f'تم إنشاء حسابك بنجاح! يمكنك الآن تسجيل الدخول.')
            return redirect('login')  # التوجيه إلى صفحة تسجيل الدخول
        else:
            messages.error(request, 'هناك مشكلة في البيانات المدخلة. يرجى المحاولة مجددًا.')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# تسجيل الدخول
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('home')  # التوجيه إلى الصفحة الرئيسية بعد تسجيل الدخول
            else:
                messages.error(request, 'بيانات الدخول غير صحيحة. يرجى التحقق من اسم المستخدم أو كلمة المرور.')
        else:
            messages.error(request, 'يرجى ملء الحقول بشكل صحيح.')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

# تسجيل الخروج
def logout_view(request):
    logout(request)
    return redirect('home')

# صفحة تعديل البيانات
@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث بياناتك بنجاح.")
            return redirect('profile')  # إعادة توجيه المستخدم إلى الصفحة الشخصية بعد التحديث
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'users/profile.html', {'form': form})
