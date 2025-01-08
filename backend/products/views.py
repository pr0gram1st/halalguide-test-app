from .models import Category, Supplier, Product, SupplierPrice, Banner, Order, Application, CartItem, Cart, Favorite
from .serializers import (
    CategorySerializer, SupplierSerializer, ProductSerializer,
    SupplierPriceSerializer, BannerSerializer, OrderSerializer, SupplierByCategorySerializer, ProductsBySupplierSerializer,
    ApplicationSerializer, CartSerializer, CartItemSerializer, FavoriteSerializer
)
from rest_framework.views import APIView
from django.db.models import Q, Count, Min
from django.db import models

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status

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

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [AllowAny]

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

    def perform_create(self, serializer):
        product = serializer.validated_data.get('product')
        supplier = serializer.validated_data.get('supplier', None)

        favorite = serializer.save(user=self.request.user)

        product.is_favorite = True
        product.save()

        if supplier:
            supplier.is_favorite = True
            supplier.save()

        return favorite

    def perform_destroy(self, instance):
        product = instance.product
        supplier = instance.supplier

        if not Favorite.objects.filter(product=product).exclude(pk=instance.pk).exists():
            product.is_favorite = False
            product.save()

        if supplier and not Favorite.objects.filter(supplier=supplier).exclude(pk=instance.pk).exists():
            supplier.is_favorite = False
            supplier.save()

        super().perform_destroy(instance)


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
        products = Product.objects.filter(suppliers__id=supplier_id)
        serializer = ProductsBySupplierSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Creates a new order.

    This endpoint allows a user to create an order for a specific product from a specific supplier.

    **Request Body Parameters:**
    - `product_id` (int): The ID of the product to be ordered (required).
    - `supplier_id` (int): The ID of the supplier providing the product (required).
    - `quantity` (int): The quantity of the product to be ordered. Defaults to `1` if not provided (optional).

    **Sample Request:**
    ```json
    {
        "product_id": 1,
        "supplier_id": 2,
        "quantity": 3,
    }
    ```

    **Sample Response (201 Created):**
    ```json
    {
        "message": "Order created successfully",
        "order_id": 10
    }
    ```

    **Response Details:**
    - `201 Created`: Order was created successfully.
    - `404 Not Found`: Either the product or the supplier was not found.
    - `400 Bad Request`: If the input data is invalid.

    **Potential Errors:**
    - `Product not found`: If the `product_id` does not exist in the database.
    - `Supplier not found`: If the `supplier_id` does not exist in the database.
    """

    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'User not authenticated'})

    product_id = request.data.get('product_id')
    supplier_id = request.data.get('supplier_id')
    quantity = request.data.get('quantity', 1)

    try:
        product = Product.objects.get(id=product_id)
        supplier = Supplier.objects.get(id=supplier_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    except Supplier.DoesNotExist:
        return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)

    total_price = product.price_retail * quantity

    order = Order.objects.create(
        user=user,
        supplier_details=supplier,
        product=product,
        quantity=quantity,
        total_cost=total_price,
    )

    return Response(
        {'message': 'Order created successfully', 'order_id': order.id},
        status=status.HTTP_201_CREATED
    )

class ListOrdersAPIView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
