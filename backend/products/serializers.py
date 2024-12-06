from rest_framework import serializers
from .models import (
    Category, Supplier, Product, SupplierPrice,
    Banner, OrderItem, Order, Cart, CartItem, Favorite
)

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    suppliers_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'suppliers_count', 'children']

    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data if children.exists() else []

    def get_suppliers_count(self, obj):
        return obj.suppliers.count()

class SupplierSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)  # Nested categories

    class Meta:
        model = Supplier
        fields = ['id', 'name', 'logo', 'rating', 'is_favourite', 'city', 'categories', 'contact_number']


class SupplierPriceSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer()  # Nested supplier data
    product = serializers.PrimaryKeyRelatedField(read_only=True)  # Avoid circular dependency

    class Meta:
        model = SupplierPrice
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    suppliers = SupplierSerializer(many=True)  # Nested supplier data

    class Meta:
        model = Product
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    category = CategorySerializer()  # Nested category data
    supplier = SupplierSerializer()
    product = ProductSerializer()

    class Meta:
        model = Banner
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Nested product data
    supplier = SupplierSerializer()  # Nested supplier data

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)  # Nested order items
    user = serializers.StringRelatedField()  # Replace with `UserSerializer()` if you want nested user data

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Nested product data

    class Meta:
        model = CartItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Replace with `UserSerializer()` for nested user data
    items = CartItemSerializer(many=True, read_only=True)  # Nested cart items

    class Meta:
        model = Cart
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Replace with `UserSerializer()` for nested user data
    product = ProductSerializer()  # Nested product data

    class Meta:
        model = Favorite
        fields = '__all__'
