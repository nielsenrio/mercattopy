from django.contrib import messages
from django.shortcuts import render, redirect
from catalog.forms import ProductForm, CategoryForm
from catalog.models import Category, Product

def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('category_list')

    else:
        form = CategoryForm()

    return render(
        request,
        'catalog/category_create.html',
        {'form': form}
    )

def category_update(request, id):
    category = Category.objects.get(id=id)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        'catalog/category_update.html',
        {
            'form': form,
            'category': category
        }
    )

def category_delete(request, id):
    category = Category.objects.get(id=id)

    if request.method == "POST":

        if Product.objects.filter(category=category).exists():
            messages.error(
                request,
                f' Exclusão não realizada! Esta Categoria possui produtos vinculados.'
            )
            return render(
                request,
                'catalog/category_delete.html',
                {'category': category}
            )

        category.delete()
        messages.success(
            request,
            f' Categoria "{category.name}" excluída com sucesso!'
        )
        return redirect('category_list')

    return render(
        request,
        'catalog/category_delete.html',
        {'category': category}
    )


def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('product_list')

    else:
        form = ProductForm()

    return render(
        request,
        'catalog/product_create.html',
        {'form': form}
    )

def product_update(request, id):
    product = Product.objects.get(id=id)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        'catalog/product_update.html',
        {
            'form': form,
            'product': product
        }
    )

def product_delete(request, id):
    product = Product.objects.get(id=id)

    if request.method == "POST":

        if product.stock > 0:
            messages.error(
                request,
                f' Exclusão não realizada! Produto em estoque!'
            )
            return render(
                request,
                'catalog/product_delete.html',
                {'product': product}
            )

        product.delete()
        messages.success(
            request,
            f' Produto "{product.name}" excluída com sucesso!'
        )
        return redirect('product_list')

    return render(
        request,
        'catalog/product_delete.html',
        {'product': product}
    )

def home(request):
    return render(request, 'base.html')


def logout(request):
    return render(request, 'auth/login.html')


def dashboard(request):
    return render(request, 'dashboard/dashboard.html')


def category_list(request):
    categories = Category.objects.all()
    query_search = request.GET.get('qs')

    if query_search:
        categories = categories.filter(
            name__icontains=query_search
        )

        if not categories.exists():
            messages.warning(
                request,
                f'Categoria não encontrada!'
            )

    return render(
        request,
        'catalog/category_list.html',
        {
            'categories': categories
        }
    )

def product_list(request):
    products = Product.objects.all()
    query_search = request.GET.get('qs')

    if query_search:
        products = products.filter(
            name__icontains=query_search
        )

        if not products.exists():
            messages.warning(
                request,
                f'Produto não encontrado!'
            )

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
