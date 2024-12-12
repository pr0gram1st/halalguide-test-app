from .models import Category, Supplier, Product, SupplierPrice, Banner, OrderItem, Order, Application
from .serializers import (
    CategorySerializer, SupplierSerializer, ProductSerializer,
    SupplierPriceSerializer, BannerSerializer, OrderItemSerializer, OrderSerializer, SupplierByCategorySerializer, ProductsBySupplierSerializer,
    ApplicationSerializer
)
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q, Count, Min
from django.db import models

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem, Favorite
from .serializers import CartSerializer, CartItemSerializer, FavoriteSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from django.utils.timezone import localtime, now
from rest_framework.generics import ListAPIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view

class ParentCategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategorySerializer

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SupplierViewSet(ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class SupplierPriceViewSet(ModelViewSet):
    queryset = SupplierPrice.objects.all()
    serializer_class = SupplierPriceSerializer


class BannerViewSet(ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer


class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def add_to_cart(self, request):
        user = request.user
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        cart, _ = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
        if not created:
            cart_item.quantity += int(quantity)
        cart_item.save()

        return Response({"message": "Item added to cart."})

    @action(detail=False, methods=["post"])
    def remove_from_cart(self, request):
        user = request.user
        product_id = request.data.get("product_id")

        cart = Cart.objects.filter(user=user).first()
        if cart:
            cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
            if cart_item:
                cart_item.delete()
                return Response({"message": "Item removed from cart."})
        return Response({"error": "Item not found in cart."}, status=404)


class FavoriteViewSet(ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def add_to_favorites(self, request):
        user = request.user
        product_id = request.data.get("product_id")

        if not product_id:
            return Response({"error": "Product ID is required."}, status=400)

        try:
            product = Product.objects.get(id=product_id)
            favorite, created = Favorite.objects.get_or_create(user=user, product=product)

            product.is_favorite = True
            product.save()

            return Response({"message": "Item added to favorites."})

        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=404)

    @action(detail=False, methods=["post"])
    def remove_from_favorites(self, request):
        user = request.user
        product_id = request.data.get("product_id")

        if not product_id:
            return Response({"error": "Product ID is required."}, status=400)

        try:
            favorite = Favorite.objects.filter(user=user, product_id=product_id).first()

            if not favorite:
                return Response({"error": "Item not found in favorites."}, status=404)

            favorite.delete()
            product = Product.objects.get(id=product_id)
            product.is_favorited = False
            product.save()

            return Response({"message": "Item removed from favorites."})

        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=404)



class SuppliersByCategoryView(APIView):
    def get(self, request):
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response({'error': 'category_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        suppliers = Supplier.objects.filter(categories__id=category_id).annotate(
            product_count=Count('products', filter=Q(products__suppliers__categories__id=category_id)),
            min_delivery_time=Min('products__supplierprice__delivery_time', filter=Q(products__suppliers__categories__id=category_id))
        )

        serializer = SupplierByCategorySerializer(suppliers, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)



class ProductsBySupplierView(APIView):
    def get(self, request, supplier_id):
        products = Product.objects.filter(suppliers__id=supplier_id).annotate(
            min_delivery_time=models.Min('supplierprice__delivery_time'),
            min_price=models.Min('supplierprice__price')
        )

        serializer = ProductsBySupplierSerializer(products, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def create_order(request):
    user = request.user
    product_id = request.data.get('product_id')
    supplier_id = request.data.get('supplier_id')
    quantity = request.data.get('quantity', 1)
    delivery_address = request.data.get('delivery_address', '')

    # Validate product and supplier existence
    try:
        product = Product.objects.get(id=product_id)
        supplier = Supplier.objects.get(id=supplier_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    except Supplier.DoesNotExist:
        return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)

    # Calculate prices
    unit_price = product.price_retail
    total_price = unit_price * quantity

    # Create OrderItem
    order_item = OrderItem.objects.create(
        product=product,
        quantity=quantity,
        unit_price=unit_price,
        total_price=total_price,
        delivery_address=delivery_address
    )

    # Create Order and add items
    order = Order.objects.create(
        user=user,
        supplier=supplier,
        delivery_date=now(),
        delivery_cost=0.0,
        total_cost=total_price,
        payment_method='cash',
        status='pending'
    )
    order.items.add(order_item)

    # Respond with success message
    return Response({'message': 'Order created successfully', 'order_id': order.id}, status=status.HTTP_201_CREATED)

class ListOrdersAPIView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
