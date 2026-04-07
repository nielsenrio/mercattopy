import logging
from django.http import HttpResponseForbidden

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from catalog.forms import ProductForm, CategoryForm
from catalog.models import Category, Product
from sales.models import SaleItem

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'base.html')

def login_view(request):
    if request.method == "POST":
        username = (request.POST.get('username') or '').strip()
        password = (request.POST.get('password') or '').strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'auth/login.html', {'error': 'Credenciais inválidas'})

    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def error_403(request, exception=None):
    try:
        if exception:
            logger.warning(
                "Erro 403 | Usuário: %s | Path: %s | Detalhes: %s",
                request.user.username if request.user.is_authenticated else 'Anônimo',
                request.path,
                str(exception)
            )

        return render(request, 'page_403.html', status=403)
    except Exception:
        logger.warning(
            "Falha ao renderizar página 403 | Usuário: %s | Path: %s | Detalhes do erro: %s",
            request.user.username if request.user.is_authenticated else 'Anônimo',
            request.path,
            str(exception)
        )

        return HttpResponseForbidden("Acesso negado. Você não tem permissão para acessar esta página.")

@login_required()
def dashboard(request):
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    inactive_products = Product.objects.filter(is_active=False).count()

    contexto = {
            'total_products': total_products,
            'total_categories': total_categories,
            'active_products': active_products,
            'inactive_products': inactive_products
        }

    return render(request, 'dashboard/dashboard.html', contexto)

@login_required
@permission_required('catalog.add_category', raise_exception=True)
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

@login_required
@permission_required('catalog.change_category', raise_exception=True)
def category_update(request, id):
    category = get_object_or_404(Category, id=id)

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

@login_required
@permission_required('catalog.delete_category', raise_exception=True)
def category_delete(request, id):
    category = get_object_or_404(Category, id=id)

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

@login_required
@permission_required('catalog.add_product', raise_exception=True)
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

@login_required
@permission_required('catalog.change_product', raise_exception=True)
def product_update(request, id):
    product = get_object_or_404(Product, id=id)

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

@login_required
@permission_required('catalog.delete_product', raise_exception=True)
def product_delete(request, id):
    product = get_object_or_404(Product, id=id)

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

        if SaleItem.objects.filter(product=product).exists():
            messages.error(
                request,
                'Exclusão não realizada! Este produto possui vendas vinculadas.'
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

@login_required
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

@login_required
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

@login_required
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    return render(
        request,
        'catalog/product_detail.html',
        {
            'product': product
        }
    )
