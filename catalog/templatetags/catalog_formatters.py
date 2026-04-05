from decimal import Decimal
from django import template

register = template.Library()

@register.filter
def phone_format(value):
    value = ''.join(filter(str.isdigit, str(value)))

    if len(value) == 11:
        return f'({value[:2]}) {value[2:7]}-{value[7:]}'
    elif len(value) == 10:
        return f'({value[:2]}) {value[2:6]}-{value[6:]}'

    return value

@register.filter
def zip_code_format(value):
    value = ''.join(filter(str.isdigit, str(value)))

    if len(value) == 8:
        return f'{value[:5]}-{value[5:]}'

    return value

@register.filter
def document_format(value):
    doc = ''.join(filter(str.isdigit, str(value)))

    if len(doc) == 11:
        # CPF
        return f'{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}'

    elif len(doc) == 14:
        # CNPJ
        return f'{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}'

    return value


@register.filter
def real_format(value):
    if value is None:
        return "R$ 0,00"

    try:
        value = Decimal(value)
    except:
        return value

    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


