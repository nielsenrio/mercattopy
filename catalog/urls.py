from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/', views.login_view, name='login'),
    path('auth/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('category/', views.category_list, name='category_list'),
    path('category/adicionar/', views.category_create, name='category_create'),
    path('category/editar/<int:id>/', views.category_update, name='category_update'),
    path('category/excluir/<int:id>/', views.category_delete, name='category_delete'),
    path('product/', views.product_list, name='product_list'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('product/adicionar/', views.product_create, name='product_create'),
    path('product/editar/<int:id>/', views.product_update, name='product_update'),
    path('product/excluir/<int:id>/', views.product_delete, name='product_delete'),
]