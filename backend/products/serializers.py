from rest_framework import serializers
from .models import Product, Cart, CartItem, Order, OrderItem, Favorite, Supplier, SupplierStatistics, Category

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'article', 'price_wholesale', 'price_retail', 'minimum_order_quantity', 'delivery_time', 'city', 'photo']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent_category']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='items.all', read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'user', 'is_active', 'items']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='items.all', read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'status', 'total_amount', 'items']

class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product']

class SupplierStatisticsSerializer(serializers.ModelSerializer):
    supplier = serializers.StringRelatedField()
    class Meta:
        model = SupplierStatistics
        fields = ['supplier', 'total_orders', 'total_items', 'total_amount']
