from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='sales_home'),
    path('customer/', views.customer_list, name='customer_list'),
    path('customer/<int:id>/', views.customer_detail, name='customer_detail'),
    path('customer/adicionar/', views.customer_create, name='customer_create'),
    path('customer/editar/<int:id>/', views.customer_update, name='customer_update'),
    path('customer/excluir/<int:id>/', views.customer_delete, name='customer_delete'),
    path('order/', views.order_list, name='order_list'),
    path('order/adicionar/', views.order_create, name='order_create'),
    path('order/editar/<int:id>/', views.order_update, name='order_update'),
    path('order/excluir/<int:id>/', views.order_delete, name='order_delete'),
]