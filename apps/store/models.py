from django.db import models
from django.utils.crypto import get_random_string

# Cart products
# Carts
# Orders
# Customers


class Category(models.Model):
    """
    Stores data for category with 1 child, related to :model:`apps.store.Product`
    """
    title = models.CharField(max_length=255, verbose_name='Name of the category')
    slug = models.SlugField(unique=True, verbose_name='Unique link for category')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_random_string(8,'0123456789') 
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Stores data for product with 1 parent and 1 child
    related to :model:`apps.store.Category`
    related to :model:`apps.store.ProductImage`
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product')
    title = models.CharField(max_length=255, verbose_name='Title of the product')
    desctiption = models.TextField(verbose_name='Description for the product')
    old_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Old price')
    new_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='New price')
    slug = models.SlugField(unique=True, verbose_name='Unique link for product')
    reveal = models.BooleanField(default=False, verbose_name='Display product if True')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Product quantity')

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = "Products"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_random_string(8,'0123456789') 
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Product name: {self.title}'


class ProductImage(models.Model):
    """
    Stores data for product image with 1 parent related to :model:`apps.store.Product`
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    main_image = models.ImageField(verbose_name='main_image', upload_to='store_images')
    image = models.ImageField(verbose_name='product image', upload_to='store_images', blank=True, null=True)

    def __str__(self):
        return f'Product images id: {self.id}'

####################################################
class Cart(models.Model):
    products = models.ManyToManyField('CartProduct', blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Total price')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return f'Cart with id: {self.id}'


class CartProduct(models.Model):
    cart = models.ForeignKey('Cart', verbose_name='Cart', on_delete=models.CASCADE, related_name='related_products')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantity')
    total_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Total price')

    def __str__(self):
        return f"Cart product: {self.id}"

    # def save(self, *args, **kwargs):
    #     self.total_price = self.qty * self.content_object.price
    #     super().save(*args, **kwargs)


class Order(models.Model):

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


    first_name = models.CharField(max_length=255, verbose_name='First name')
    last_name = models.CharField(max_length=255, verbose_name='Last name')
    phone = models.CharField(max_length=20, verbose_name='Phone')
    cart = models.ForeignKey('Cart', verbose_name='Cart', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Address', null=True, blank=True)
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
    comment = models.TextField(verbose_name='Comment for order', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Order created date')
    order_date = models.DateField(verbose_name='Date of receipt of the order ', default=timezone.now)

    def __str__(self):
        return f'Order with id: {self.id}'
