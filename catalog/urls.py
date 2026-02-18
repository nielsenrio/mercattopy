from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('category/', views.category_list, name='category_list'),
    path('category/register/', views.category_registration, name='category_registration'),
    path('product/', views.product_list, name='product_list'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('product/register/', views.product_registration, name='product_registration'),
]