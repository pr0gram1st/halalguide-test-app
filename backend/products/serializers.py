from rest_framework import serializers
from .models import (
    Category, Supplier, Product, SupplierPrice,
    Banner, Order, Cart, CartItem, Favorite, Application, Delivery
)

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    suppliers_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'suppliers_count', 'children']

    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data if children.exists() else []

    def get_suppliers_count(self, obj):
        return obj.suppliers.count()




class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'logo', 'rating', 'city', 'contact_number']


class SupplierPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierPrice
        fields = ['supplier', 'product', 'price', 'delivery_time']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'article', 'price_retail', 'price_wholesale',
            'min_order_quantity', 'delivery_time', 'city', 'description', 'photo', 'is_favorite'
        ]


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'category', 'supplier', 'product', 'photo']


class OrderSerializer(serializers.ModelSerializer):
    supplier_details = SupplierSerializer(many=True, read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'supplier_details', 'product', 'quantity', 'total_cost']

    def create(self, validated_data):
        order = Order.objects.create(**validated_data)
        return order


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'updated_at', 'items']


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product', 'supplier']


class ApplicationSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True)

    class Meta:
        model = Application
        fields = [
            'id', 'user', 'orders', 'payment_method',
            'status', 'delivery_date', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        orders_data = validated_data.pop('orders')
        application = Application.objects.create(**validated_data)
        for order_data in orders_data:
            order = Order.objects.create(**order_data)
            application.orders.add(order)
        return application


class DeliverySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    address = serializers.CharField(max_length=255)
    contact_number = serializers.CharField(max_length=15)
    status = serializers.ChoiceField(choices=Delivery.STATUS_CHOICES, default='PENDING')
    delivery_date = serializers.DateField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Delivery
        fields = ['id', 'user', 'address', 'contact_number', 'status', 'delivery_date', 'created_at', 'updated_at']


class SupplierByCategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField()
    min_delivery_time = serializers.CharField()
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = ['id', 'name', 'city', 'logo', 'product_count', 'min_delivery_time']

    def get_logo(self, obj):
        request = self.context.get('request')
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        return None


class ProductsBySupplierSerializer(serializers.ModelSerializer):
    min_delivery_time = serializers.CharField()
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'article', 'photo', 'min_delivery_time', 'min_price']

    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None
