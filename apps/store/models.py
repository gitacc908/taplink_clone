from django.utils import timezone
from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    """
    Stores data for category with 1 child, related to :model:`apps.store.Product`
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255,
                             verbose_name='Name of the category')
    slug = models.SlugField(unique=True,
                            verbose_name='Unique link for category')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = "Categories"
        ordering = ['-id']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_random_string(8, '0123456789')
        super().save(*args, **kwargs)


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, 
                                blank=True, on_delete=models.CASCADE)
    device = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        if self.user:
            return str(self.user.phone_number)
        else:
            return self.device


class Product(models.Model):
    """
    Stores data for product with 1 parent and 1 child
    related to :model:`apps.store.Category`
    related to :model:`apps.store.ProductImage`
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='product')
    main_image = models.ImageField(verbose_name='main_image',
                                   upload_to='store_images')
    title = models.CharField(max_length=255,
                             verbose_name='Title of the product')
    description = models.TextField(verbose_name='Description for the product')
    price = models.DecimalField(max_digits=9, decimal_places=2,
                                verbose_name='Price')
    discount_price = models.DecimalField(max_digits=9, decimal_places=2,
                                verbose_name='Discount', null=True, blank=True)
    slug = models.SlugField(unique=True,
                            verbose_name='Unique link for product')
    in_stock = models.BooleanField(default=False,
                                   verbose_name='In stock')
    quantity = models.PositiveIntegerField(default=1,
                                           verbose_name='Product quantity')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = "Products"
        ordering = ('-created',)

    def __str__(self):
        return f'Title: {self.title}, Owner: {self.owner}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_random_string(8, '0123456789')
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={
            "slug" : self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("add_to_cart", kwargs={
            "slug" : self.slug
            })

    def get_remove_from_cart_url(self):
        return reverse("remove_from_cart", kwargs={
            "slug" : self.slug
        })


class ProductImage(models.Model):
    """
    Stores data for product image with 1 parent related to :model:`apps.store.Product`
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='product_images')
    image = models.ImageField(verbose_name='product image',
                              upload_to='store_images', blank=True, null=True)

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = "Images"

    def __str__(self):
        return f'Image for product: {self.product}, id: {self.id}'


class CartProduct(models.Model):
    """
    Stores data with cart product cretendials.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Cart Product',
                    on_delete=models.CASCADE, related_name='related_products')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantity')
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f'Cart Product: {self.product.title}, Quantity: {self.quantity}'

    def get_total_item_price(self):
        return self.quantity * self.product.price

    def get_discount_item_price(self):
        return self.quantity * self.product.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_discount_item_price()

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    """
    Stores data for order model with cart credentials.
    """
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    PURCHASE_BY_CARD = 'card'
    PURCHASE_BY_CASH = 'cash'

    STATUS_CHOICES = (
        (STATUS_NEW, 'New order'),
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_READY, 'Ready'),
        (STATUS_COMPLETED, 'Completed')
    )

    BUYING_TYPE_CHOICES = (
        (PURCHASE_BY_CARD, 'Purchase by card'),
        (PURCHASE_BY_CASH, 'Purchase by cash')
    )
    customer = models.ForeignKey(Customer,
                             on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='First name')
    last_name = models.CharField(max_length=255, verbose_name='Last name')
    phone = models.CharField(max_length=20, verbose_name='Phone')
    products = models.ManyToManyField(CartProduct)
    address = models.CharField(max_length=1024, verbose_name='Address',
                               null=True, blank=True)
    status = models.CharField(
        max_length=100,
        verbose_name='Order status',
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    buying_type = models.CharField(
        max_length=100,
        verbose_name='Purchase type',
        choices=BUYING_TYPE_CHOICES,
        default=PURCHASE_BY_CARD
    )
    comment = models.TextField(verbose_name='Comment for order',
                               null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True,
                                      verbose_name='Order created date')
    ordered_date = models.DateField(verbose_name='Date of receipt of the order',
                                  default=timezone.now)

    def __str__(self):
        if self.customer.device:
            return f'Id: {self.id} Device: {self.customer.device}'
        return f'Id: {self.id}, Customer: {self.customer.user.phone_number}'
    
    def get_total(self):
        return sum([cart_product.get_final_price() 
                    for cart_product in self.products.all()])

    def get_cart_items(self):
        return sum([1 for item in self.products.all()])
