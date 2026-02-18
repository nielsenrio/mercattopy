from django import forms
from django.core.exceptions import ValidationError
from catalog.models import Category, Product

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Nome da categoria',
                'class': 'form-control'
            }),

            'description': forms.TextInput(attrs={
                'placeholder': 'Descrição da categoria',
                'class': 'form-control'
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

        labels = {
            'name': 'Nome',
            'description': 'Descrição',
            'is_active': 'Status (Ativo)'
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()

        if not name:
            raise ValidationError(
                'Informe o nome da categoria.'
            )

        return name

    def clean_description(self):
        description = self.cleaned_data.get('description', '').strip()

        if not description:
            raise ValidationError(
                'A descrição precisa ser preenchida, não pode ser em branco.'
            )

        return description


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'stock', 'is_active']

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Nome do produto',
                'class': 'form-control'
            }),

            'category': forms.Select(attrs={
                'class': 'form-select'
            }),

            'price': forms.NumberInput(attrs={
                'placeholder': 'Preço do produto',
                'class': 'form-control',
            }),

            'stock': forms.NumberInput(attrs={
                'placeholder': 'Quantitativo em estoque',
                'class': 'form-control'
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

        labels = {
            'name': 'Nome',
            'category': 'Categoria',
            'price' : 'Preço',
            'stock' : 'Estoque',
            'is_active': 'Status (Ativo)'
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()

        if len(name) <= 2:
            raise ValidationError(
                'Informe o nome do produto com pelo menos 3 letras!!!'
            )

        return name


    def clean_price(self):
        price = self.cleaned_data.get('price')

        if price is None or price <= 0:
            raise ValidationError(
                'O preço do produto precisa ser maior do que ZERO.'
            )

        return price