from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),  # مسار التسجيل
    path('login/', views.login_view, name='login'),  # مسار تسجيل الدخول
    path('logout/', views.logout_view, name='logout'),  # مسار تسجيل الخروج
    path('profile/', views.profile, name='profile'),  # صفحة تعديل البيانات
]

