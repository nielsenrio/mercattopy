import re
from django import forms
from django.core.exceptions import ValidationError
from sales.models import Customer, Sale, SaleItem
from catalog.models import Product

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'type', 'document', 'email', 'phone', 'city', 'state', 'zip_code', 'is_active']
        error_messages = {
            'document': {
                'unique': 'Já existe um cliente com este documento.'
            }
        }

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Digite seu nome completo',
                'class': 'form-control'
            }),

            'type': forms.Select(attrs={
                'class': 'form-select'
            }),

            'document': forms.TextInput(attrs={
                'placeholder': 'Digite o CPF ou CNPJ',
                'class': 'form-control'
            }),

            'email': forms.EmailInput(attrs={
                'placeholder': 'Digite seu email',
                'class': 'form-control'

            }),

            'phone': forms.TextInput(attrs={
                'placeholder': '(00) 00000-0000',
                'class': 'form-control'
            }),

            'zip_code': forms.TextInput(attrs={
                'placeholder': '00000-000',
                'class': 'form-control'
            }),

            'city': forms.TextInput(attrs={
                'placeholder': 'Cidade ou Município',
                'class': 'form-control'
            }),

            'state': forms.TextInput(attrs={
                'placeholder': 'UF',
                'class': 'form-control'
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

        labels = {
            'name': 'Nome',
            'type': 'Tipo',
            'document': 'Documento',
            'email': 'Email',
            'phone': 'Telefone',
            'zip_code': 'CEP',
            'city': 'Cidade',
            'state': 'Estado',
            'is_active': 'Status (Ativo)'
        }

    def clean_zip_code(self):
        zip_code = (self.cleaned_data.get('zip_code') or '').strip()

        if len(zip_code) != 9 or not zip_code.replace('-', '').isdigit():
            raise ValidationError(
                'O CEP deve estar no formato 00000-000.'
            )

        zip_code = re.sub(r'\D', '', zip_code)

        return zip_code

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()

        if len(phone) < 10 or not phone.replace('(', '').replace(')', '').replace('-', '').replace(' ',
                                                                                                         '').isdigit():
            raise ValidationError(
                'O telefone deve conter pelo menos 10 dígitos e estar no formato (00) 00000-0000.'
            )

        phone = re.sub(r'\D', '', phone)

        return phone

    def clean_name(self):
        name = (self.cleaned_data.get('name') or '').strip()

        if len(name) < 3:
            raise ValidationError(
                'Informe o nome do cliente com pelo menos 3 letras.'
            )

        return name


    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()

        if not email:
            raise ValidationError('O email é obrigatório.')

        return email


    def clean_document(self):
        document = (self.cleaned_data.get('document') or '').strip()

        if not document:
            raise ValidationError('O número de CPF ou CNPJ é obrigatório.')

        document = re.sub(r'\D', '', document)

        if len(document) > 14:
            raise ValidationError('Preenchimento excedido. CNPJ deve conter 14 dígitos.')
        elif 13 >= len(document) > 11:
            raise ValidationError('CNPJ deve conter 14 dígitos.')
        elif len(document) < 11:
            raise ValidationError('Preenchimento incompleto. CPF deve conter 11 dígitos.')

        return document


class SaleForm(forms.ModelForm):

    customer = forms.ModelChoiceField(
        queryset=Customer.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Cliente'
    )

    class Meta:
        model = Sale
        fields = ['customer', 'payment_method', 'status_order']

        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),

            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),

            'status_order': forms.Select(attrs={
                'class': 'form-select',
                'disable': 'disable'
            }),
        }

        labels = {
            'payment_method': 'Forma de Pagamento',
            'status_order': 'Status da Venda',
            'total': 'Total da Venda',
        }


class SaleItemForm(forms.ModelForm):

    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Produto'
    )

    class Meta:
        model = SaleItem
        fields = ['product', 'quantity']

        widgets = {
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'Digite a quantidade',
                'class': 'form-control',
                'min': 1,
            }),
        }

        labels = {
            'quantity': 'Quantidade',
            'unit_price': 'Preço Unitário',
            'subtotal': 'Subtotal',
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        product = self.cleaned_data.get('product')

        if not product.is_active:
            raise ValidationError('Produto inativo.')

        if quantity <= 0:
            raise ValidationError('Valor deve ser maior do que zero.')

        if product.stock != 0:
            if quantity > product.stock:
                raise ValidationError(
                    f'Estoque insuficiente. Disponível: {product.stock}'
                )

        return quantity
