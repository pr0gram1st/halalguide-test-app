from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import localtime, now

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    logo = models.ImageField(upload_to='category_logos/', null=True, blank=True)  # Added logo field

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='supplier_logos/')
    rating = models.FloatField()
    is_favourite = models.BooleanField(default=False)
    city = models.CharField(max_length=255)
    categories = models.ManyToManyField(Category, related_name='suppliers')
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    article = models.CharField(max_length=100)
    price_wholesale = models.DecimalField(max_digits=10, decimal_places=2)
    price_retail = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_quantity = models.PositiveIntegerField()
    delivery_time = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    description = models.TextField()
    characteristics = models.JSONField()
    photo = models.ImageField(upload_to='product_photos/')
    suppliers = models.ManyToManyField(
        Supplier,
        through='SupplierPrice',
        related_name='products'
    )

    def __str__(self):
        return self.name

class SupplierPrice(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.supplier.name} - {self.product.name}"

class Banner(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    photo = models.ImageField(upload_to='banners/')

    def __str__(self):
        return f"Banner for {self.category or self.supplier or self.product}"


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Order(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('non-cash', 'Non-Cash'),
        ('online', 'Online')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivering', 'Delivering'),
        ('completed', 'Completed')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True)
    items = models.ManyToManyField(OrderItem, related_name='orders')
    delivery_date = models.DateTimeField()
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    comment = models.TextField(null=True, blank=True)
    supplier_details = models.ManyToManyField(Supplier, related_name='orders')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order by {self.user.username} - {self.status}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username} (Last updated: {localtime(self.updated_at)})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"


class Favorite(models.Model):
    user = models.ForeignKey(User, related_name="favorites", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="favorited_by", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} favorited by {self.user.username}"

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deliveries")
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    delivery_date = models.DateField(default=now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery for {self.user.username} on {self.delivery_date} ({self.get_status_display()})"


class SupplierStatistics(models.Model):
    supplier = models.CharField(max_length=255)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="supplier_statistics")
    total_supplied = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    last_supply_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Statistics for {self.supplier} (Product: {self.product.name})"

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    orders = models.ManyToManyField(Order, related_name='applications')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application by {self.user.username} on {localtime(self.created_at)}"