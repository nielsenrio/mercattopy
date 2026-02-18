from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)


    class Meta:
        db_table = 'Category'

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
    )

    class Meta:
        db_table = 'Product'

    def __str__(self):
        return f'{self.name} - {self.category.name} - {self.price} - {self.stock}'