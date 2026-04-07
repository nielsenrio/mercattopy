from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from sales.forms import CustomerForm, SaleForm, SaleItemForm
from sales.models import Customer, Sale, SaleItem

@login_required
def home(request):
    sales = Sale.objects.filter(status_order='Completed').select_related('customer').prefetch_related('items')

    return render(
        request,
        'sales_home.html',
        {'sales': sales}
    )


@login_required
def customer_list(request):
    customers = Customer.objects.all()
    query_search = request.GET.get('qs')

    if query_search:
        customers = customers.filter(
                name__icontains=query_search
            )

        if not customers.exists():
            messages.warning(
                request,
                f'Cliente não encontrado!'
            )

    return render(
        request,
        'customer/customer_list.html',
        {'customers': customers}
    )

@login_required
@permission_required('sales.add_customer', raise_exception=True)
def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()

    return render(
        request,
        'customer/customer_create.html',
        {'form': form}
    )

@login_required
@permission_required('sales.change_customer', raise_exception=True)
def customer_update(request, id):
    customer = get_object_or_404(Customer, id=id)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)

        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)

    return render(
        request,
        'customer/customer_update.html',
        {'form': form,'customer': customer}
    )

@login_required
@permission_required('sales.delete_customer', raise_exception=True)
def customer_delete(request, id):
    customer = get_object_or_404(Customer, id=id)

    if request.method == "POST":

        if customer.is_active:
            messages.error(
                request,
                f' Exclusão não realizada! Este Cliente está ativo.'
            )
            return render(
                request,
                'customer/customer_delete.html',
                {'customer': customer}
            )

        if Sale.objects.filter(customer=customer).exists():
            messages.error(
                request,
                'Exclusão não realizada! Este cliente possui vendas vinculadas.'
            )
            return render(
                request,
                'customer/customer_delete.html',
                {'customer': customer}
            )

        customer.delete()
        messages.success(
            request,
            f' Cliente "{customer.name}" excluído com sucesso!'
        )
        return redirect('customer_list')

    return render(
        request,
        'customer/customer_delete.html',
        {'customer': customer}

    )

@login_required
@permission_required('sales.view_customer', raise_exception=True)
def customer_detail(request, id):
    customer = get_object_or_404(Customer, id=id)

    return render(
        request,
        'customer/customer_detail.html',
        {'customer': customer}
    )

@login_required
def order_list(request):
    sales = Sale.objects.all()
    sale_items = SaleItem.objects.all()
    query_search = request.GET.get('qs')

    if query_search:
        sales = Sale.objects.filter(
            customer__name__icontains=query_search
        )

        if not sales.exists():
            messages.warning(
                request,
                f'Pedido do cliente "{query_search}" não encontrado!'
            )

    return render(
        request,
        'order/order_list.html',
        {'sales': sales,'sale_items': sale_items}
    )

@login_required
@permission_required('sales.add_sale', raise_exception=True)
def order_create(request):

    if request.method == 'POST':
        sale_form = SaleForm(request.POST)
        item_form = SaleItemForm(request.POST)

        if sale_form.is_valid() and item_form.is_valid():

            product = item_form.cleaned_data['product']
            quantity = item_form.cleaned_data['quantity']

            if not quantity or quantity <= 0:
                messages.warning(request, 'A quantidade deve ser maior que zero.')

                return render(request, 'order/order_create.html', {
                    'sale_form': sale_form,
                    'item_form': item_form
                })

            if quantity > product.stock:
                messages.error(
                    request,
                    f'Estoque insuficiente para "{product.name}". Disponível: {product.stock}'
                )
                return render(
                    request,
                    'order/order_create.html',
                    {'sale_form': sale_form,'item_form': item_form}
                )

            with transaction.atomic():

                sale = sale_form.save(commit=False) #salva 1a venda sempre como pendente
                sale.status_order = 'Pending'
                sale.total = 0
                sale.save()

                sale_item = item_form.save(commit=False) #add o item
                sale_item.sale = sale
                sale_item.unit_price = product.price
                sale_item.subtotal = product.price * quantity

                sale_item.save()

                product.stock -= quantity #update estoque
                product.save()

                sale.total += sale_item.subtotal #update total
                sale.save()

                messages.success(request, 'Pedido criado com sucesso!')
                return redirect('order_list')

    else:
        sale_form = SaleForm()
        item_form = SaleItemForm()

    return render(
        request,
        'order/order_create.html',
        {'sale_form': sale_form,'item_form': item_form}
    )

@login_required
@permission_required('sales.change_sale', raise_exception=True)
def order_update(request, id):
    sale = get_object_or_404(Sale, id=id)
    item = sale.items.get()

    if sale.status_order in ['Canceled', 'Completed']:
        tipo_order = 'Pedido' if sale.status_order == 'Canceled' else 'Venda'
        messages.error(
            request,
            f'{tipo_order} "{sale.get_status_order_display()}", não pode ser alterado!'
        )
        return redirect('order_list')

    if request.method == 'POST':
        sale_form = SaleForm(request.POST, instance=sale)
        item_form = SaleItemForm(request.POST, instance=item)

        old_status = sale.status_order
        old_costumer = item.sale.customer
        old_product = item.product
        old_quantity = item.quantity
        old_pay_method = sale.payment_method

        if sale_form.is_valid() and item_form.is_valid():

            try:
                with transaction.atomic():

                    sale = sale_form.save(commit=False)
                    new_status = sale.status_order

                    new_item = item_form.save(commit=False)
                    new_quantity = new_item.quantity
                    new_product = new_item.product

                    if new_product != old_product:
                        messages.warning(request, 'Produto não pode ser alterado.')
                        return redirect('order_list')

                    if old_status == 'Pending' and new_status == 'Pending':
                        product = old_product
                        item.quantity = old_quantity
                        product.save()
                        sale.customer = old_costumer
                        sale.payment_method = old_pay_method
                        sale.save()
                        messages.warning(request, 'Pedido pendente, valores inalterados!')
                        return redirect('order_list')

                    if old_status == 'Pending' and new_status == 'Canceled':
                        product = old_product
                        product.stock += old_quantity
                        item.quantity = old_quantity
                        product.save()

                        sale.status_order = 'Canceled'
                        sale.payment_method = old_pay_method
                        sale.total = 0
                        sale.save()

                        messages.success(request, 'Pedido cancelado e estoque devolvido!')
                        return redirect('order_list')

                    if old_status == 'Pending' and new_status == 'Completed':
                        product = old_product
                        item.quantity = old_quantity
                        product.save()
                        sale.customer = old_costumer
                        item.subtotal = (product.price * item.quantity)
                        sale.status_order = 'Completed'
                        sale.save()

                        messages.success(request, 'Venda concluída com sucesso!')
                        return redirect('order_list')

            except Exception:
                messages.error(request, 'Erro ao atualizar o pedido.')
                return redirect('order_update', id=sale.id)

    else:
        sale_form = SaleForm(instance=sale)
        item_form = SaleItemForm(instance=item)

    return render(
        request,
        'order/order_update.html',
        {'sale_form': sale_form,'item_form': item_form,'sale': sale}
    )

@login_required
@permission_required('sales.delete_sale', raise_exception=True)
def order_delete(request, id):
    sale = get_object_or_404(Sale, id=id)
    item = sale.items.get()

    if sale.status_order in ['Canceled', 'Completed']:
        tipo_order = 'Pedido' if sale.status_order == 'Canceled' else 'Venda'
        messages.error(
            request,
            f'{tipo_order} "{sale.get_status_order_display()}", não pode ser excluído!'
        )
        return redirect('order_list')

    if request.method == 'POST':
        try:
            with (transaction.atomic()):
                product = item.product
                product.stock += item.quantity
                product.save()
                sale.delete()

            messages.success(request, 'Estoque reposto. Pedido excluído com sucesso!')
            return redirect('order_list')

        except Exception:
            messages.error(request, 'Erro ao excluir a venda.')

    return render(
        request,
        'order/order_delete.html',
        {'sale': sale}
    )

