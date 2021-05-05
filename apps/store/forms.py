from django import forms
from betterforms.multiform import MultiModelForm
from .models import Category, Product, ProductImage, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('category', 'main_image', 'title', 'description', 'price',
                  'discount_price', 'in_stock', 'quantity')


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ('image',)


class ProductMultiModelForm(MultiModelForm):
    form_classes = {'product': ProductForm,
                    'product_image': ProductImageForm}


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'phone',
                  'address', 'buying_type', 'comment')
