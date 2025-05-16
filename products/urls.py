from django.urls import path
from .views import Productlistview ,ProductUpdateView ,ProductDeleteView ,CategoryCreateView

urlpatterns = [
    path('',Productlistview.as_view(),name='product-list'),
    # path('add/',ProductCreateView.as_view(),name = 'product-add'),
    path('<int:pk>/edit/',ProductUpdateView.as_view(),name='product-edit'),
    path('<int:pk>/delete/',ProductDeleteView.as_view(),name='product-delete'),
     path('categories/add/', CategoryCreateView.as_view(), name='category-add')
]
