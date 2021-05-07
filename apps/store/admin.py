from django.contrib import admin
from .models import (
    Category, Product, CartProduct, Order, ProductImage
)


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CartProduct)
admin.site.register(Order)
admin.site.register(ProductImage)
