from .models import Category, Supplier, Product, SupplierPrice, Banner, OrderItem, Order
from .serializers import (
    CategorySerializer, SupplierSerializer, ProductSerializer,
    SupplierPriceSerializer, BannerSerializer, OrderItemSerializer, OrderSerializer, SupplierByCategorySerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Min
from django.db import models

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem, Favorite
from .serializers import CartSerializer, CartItemSerializer, FavoriteSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response

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

        Favorite.objects.get_or_create(user=user, product_id=product_id)
        return Response({"message": "Item added to favorites."})

    @action(detail=False, methods=["post"])
    def remove_from_favorites(self, request):
        user = request.user
        product_id = request.data.get("product_id")

        favorite = Favorite.objects.filter(user=user, product_id=product_id).first()
        if favorite:
            favorite.delete()
            return Response({"message": "Item removed from favorites."})
        return Response({"error": "Item not found in favorites."}, status=404)


class SuppliersByCategoryView(APIView):
    def get(self, request):
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response({'error': 'category_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Query suppliers filtered by category and annotate with product count and minimum delivery time
        suppliers = Supplier.objects.filter(categories__id=category_id).annotate(
            product_count=models.Count('products'),
            min_delivery_time=models.Min('products__supplierprice__delivery_time')
        )

        # Serialize the data with context for absolute URI
        serializer = SupplierByCategorySerializer(suppliers, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductsBySupplierView(APIView):
    def get(self, request, supplier_id):
        products = Product.objects.filter(suppliers__id=supplier_id).annotate(
            min_delivery_time=models.Min('supplierprice__delivery_time'),
            min_price=models.Min('supplierprice__price')
        ).values(
            'id', 'name', 'article', 'photo', 'min_delivery_time', 'min_price'
        )

        return Response(products, status=status.HTTP_200_OK)
