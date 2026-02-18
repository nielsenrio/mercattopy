from django.shortcuts import render, redirect
from catalog.forms import ProductForm, CategoryForm
from catalog.models import Category, Product

def category_registration(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('category_list')

    else:
        form = CategoryForm()

    return render(
        request,
        'catalog/register/category_registration.html',
        {'form': form}
    )

def product_registration(request):
    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('product_list')

    else:
        form = ProductForm()

    return render(
        request,
        'catalog/register/product_registration.html',
        {'form': form}
    )


def home(request):
    return render(request, 'base.html')


def logout(request):
    return render(request, 'auth/login.html')


def dashboard(request):
    return render(request, 'dashboard/dashboard.html')


def category_list(request):
    categories = Category.objects.all()

    return render(
        request,
        'catalog/category_list.html',
        {
            'categories': categories
        }
    )

def product_list(request):
    products = Product.objects.all()

    return render(
        request,
        'catalog/product_list.html',
        {
            'products': products
        }
    )

def product_detail(request, id):
    product = Product.objects.get(id=id)

    return render(
        request,
        'catalog/product_detail.html',
        {
            'product': product
        }
    )
