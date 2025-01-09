from rest_framework import serializers
from .models import (
    Category, Supplier, Product, SupplierPrice,
    Banner, Order, Cart, CartItem, Favorite, Application, Delivery
)
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    suppliers_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data if children.exists() else []

    def get_suppliers_count(self, obj):
        return obj.suppliers.count()




class SupplierSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Supplier
        fields = "__all__"


class SupplierPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierPrice
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    suppliers = SupplierSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = "__all__"


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'category', 'supplier', 'product', 'photo']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class OrderSerializer(serializers.ModelSerializer):
    supplier_details = SupplierSerializer(read_only=True)
    product = ProductSerializer(read_only=True)  # Use nested Product representation
    user = UserSerializer(read_only=True)  # Use nested User representation
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
    user = serializers.ReadOnlyField(source='user.id')
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  # Expecting the product ID
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), required=False)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product', 'supplier']

    def validate(self, data):
        """
        Ensure the user cannot add the same product from the same supplier more than once.
        """
        user = self.context['request'].user
        product = data.get('product')
        supplier = data.get('supplier')

        if Favorite.objects.filter(user=user, product=product, supplier=supplier).exists():
            raise serializers.ValidationError(
                "You have already added this product from this supplier to your favorites."
            )

        return data

    def to_representation(self, instance):
        """
        Customize the serialized output to include nested product and supplier details.
        """
        representation = super().to_representation(instance)

        if isinstance(instance, Favorite):
            representation['product'] = ProductCompactSerializer(instance.product, context=self.context).data
            if instance.supplier:
                representation['supplier'] = SupplierCompactSerializer(instance.supplier, context=self.context).data

        return representation

# for favorite
class ProductCompactSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'article', 'photo', 'is_favorite']

    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None

# for favorite
class SupplierCompactSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = ['id', 'name', 'logo', 'rating', 'is_favourite', 'city', 'contact_number', 'is_favourite']

    def get_logo(self, obj):
        request = self.context.get('request')
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        return None



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
        fields = "__all__"

    def get_logo(self, obj):
        request = self.context.get('request')
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        return None


class ProductsBySupplierSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None
