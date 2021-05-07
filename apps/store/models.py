import random
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from autoslug import AutoSlugField
from django.db.models.signals import post_save
from django.dispatch import receiver
from .choices import (
    STATUS_NEW, STATUS_IN_PROGRESS, STATUS_READY, STATUS_COMPLETED,
    PURCHASE_BY_CARD, PURCHASE_BY_CASH, STATUS_CHOICES,
    BUYING_TYPE_CHOICES
)


User = get_user_model()


class Category(models.Model):
    """
    Stores data for category with 1 child,
    related to :model:`apps.store.Product`
    """
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    title = models.CharField(
        max_length=255, verbose_name='Name of the category'
    )
    slug = AutoSlugField(
        populate_from='title', unique=True
    )

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = "Categories"
        ordering = ['-id']

    def __str__(self):
        return self.title


class Product(models.Model):
    """
    Stores data for product with 1 parent and 1 child
    related to :model:`apps.store.Category`
    related to :model:`apps.store.ProductImage`
    """
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name='product', blank=True, null=True
    )
    main_image = models.ImageField(
        verbose_name='main_image', upload_to='store_images/'
    )
    title = models.CharField(
        max_length=255, verbose_name='Title of the product'
    )
    description = models.TextField(
        verbose_name='Description for the product'
    )
    price = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name='Price'
    )
    discount_price = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name='Discount',
        null=True, blank=True
    )
    slug = AutoSlugField(
        populate_from='title', unique=True
    )
    in_stock = models.BooleanField(
        default=False, verbose_name='In stock'
    )
    quantity = models.PositiveIntegerField(
        default=1, verbose_name='Product quantity'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = "Products"
        ordering = ('-created',)

    def __str__(self):
        return f'Title: {self.title}, Owner: {self.owner}'

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("add_to_cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("remove_from_cart", kwargs={"slug": self.slug})


class ProductImage(models.Model):
    """
    Stores data for product image with 1 parent
    related to :model:`apps.store.Product`
    """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='product_images'
    )
    image = models.ImageField(
        verbose_name='product image',
        upload_to='store_images/'
    )

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = "Images"

    def __str__(self):
        return f'Image for product: {self.product}, id: {self.id}'


class CartProduct(models.Model):
    """
    Stores data with cart product cretendials.
    """
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, verbose_name='Cart Product',
        on_delete=models.CASCADE,
        related_name='related_products'
    )
    quantity = models.PositiveIntegerField(
        default=1, verbose_name='Quantity'
    )

    def __str__(self):
        return f'Cart Product: {self.product.title}, Quantity: {self.quantity}'

    def get_total_item_price(self):
        return self.quantity * self.product.price

    def get_discount_item_price(self):
        if self.product.discount_price:
            return self.quantity * self.product.discount_price
        return 'No discount'

    def get_amount_saved(self):
        if self.product.discount_price:
            return self.get_total_item_price() - self.get_discount_item_price()
        return 'No discount'

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    """
    Stores data for order model with cart credentials.
    """
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    first_name = models.CharField(
        max_length=255, verbose_name='First name'
    )
    last_name = models.CharField(
        max_length=255, verbose_name='Last name'
    )
    phone = models.CharField(
        max_length=20, verbose_name='Phone'
    )
    products = models.ManyToManyField(CartProduct)
    address = models.CharField(
        max_length=1024, verbose_name='Address'
    )
    status = models.PositiveSmallIntegerField(
        verbose_name='Order status',
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    buying_type = models.PositiveSmallIntegerField(
        verbose_name='Purchase type',
        choices=BUYING_TYPE_CHOICES,
        default=PURCHASE_BY_CARD
    )
    comment = models.TextField(
        verbose_name='Comment for order'
    )
    created_at = models.DateTimeField(
        verbose_name='Order created date',
        auto_now=True
    )
    ordered_date = models.DateTimeField(
        verbose_name='Date of receipt of the order',
        auto_now=True
    )

    def __str__(self):
        return f'Id: {self.id}, Customer: {self.customer.phone_number}'

    def get_total(self):
        return sum(
            [cart_product.get_final_price()
             for cart_product in self.products.all()]
        )

    def get_cart_items(self):
        return self.products.count()
