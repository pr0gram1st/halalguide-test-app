from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent_category = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='supplier_logos/')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    def __str__(self):
        return self.name

class Product(models.Model):
    supplier = models.ForeignKey(Supplier, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price_wholesale = models.DecimalField(max_digits=10, decimal_places=2)
    price_retail = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_quantity = models.PositiveIntegerField()
    delivery_time = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='product_photos/')
    article = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, related_name="carts", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Cart {self.id} - {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="cart_items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Favorite(models.Model):
    user = models.ForeignKey(User, related_name="favorites", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="favorites", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} (Favorite)"

class Order(models.Model):
    user = models.ForeignKey(User, related_name="orders", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status_choices = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('shipped', 'Shipped')
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='in_progress')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Delivery(models.Model):
    order = models.ForeignKey(Order, related_name="delivery", on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    delivery_date = models.DateTimeField()
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Delivery for Order {self.order.id}"

class SupplierStatistics(models.Model):
    supplier = models.ForeignKey(Supplier, related_name="statistics", on_delete=models.CASCADE)
    total_orders = models.PositiveIntegerField(default=0)
    total_items = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Statistics for {self.supplier.name}"

