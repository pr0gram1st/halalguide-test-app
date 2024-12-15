from rest_framework import serializers
from .models import (
    Category, Supplier, Product, SupplierPrice,
    Banner, OrderItem, Order, Cart, CartItem, Favorite, Application
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
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = ['id', 'name', 'logo', 'rating', 'is_favourite', 'city', 'categories', 'contact_number']

    def get_categories(self, obj):
        parent_categories = obj.categories.filter(parent__isnull=True)
        return CategorySerializer(parent_categories, many=True).data


class SupplierPriceSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer()
    product = serializers.PrimaryKeyRelatedField(read_only=True)

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


class ApplicationSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True)  # Nested serializer

    class Meta:
        model = Application
        fields = ['id', 'user', 'orders', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        orders_data = validated_data.pop('orders', [])
        application = Application.objects.create(**validated_data)

        # Create or associate orders with this application
        for order_data in orders_data:
            order = Order.objects.get(id=order_data['id'])  # Get existing orders
            application.orders.add(order)

        return application

    def update(self, instance, validated_data):
        orders_data = validated_data.pop('orders', [])
        instance.orders.clear()  # Remove existing associations
        for order_data in orders_data:
            order = Order.objects.get(id=order_data['id'])
            instance.orders.add(order)

        instance.save()
        return instance

#b essets