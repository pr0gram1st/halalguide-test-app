from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from .models import Product, Cart, CartItem, Order, OrderItem, Favorite, Supplier, SupplierStatistics, Category
from .serializers import ProductSerializer, CartSerializer, OrderSerializer, FavoriteSerializer, \
    SupplierStatisticsSerializer, CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@api_view(['GET', 'POST'])
def cart_detail(request):
    user = request.user
    if request.method == 'GET':
        cart, created = Cart.objects.get_or_create(user=user, is_active=True)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    elif request.method == 'POST':
        cart, created = Cart.objects.get_or_create(user=user, is_active=True)
        product = Product.objects.get(id=request.data['product_id'])
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += request.data['quantity']
        cart_item.save()
        return Response({'status': 'Cart updated'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_cart_item(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart_item.quantity = request.data['quantity']
    cart_item.save()
    return Response({'status': 'Cart item updated'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def delete_cart_item(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart_item.delete()
    return Response({'status': 'Cart item deleted'}, status=status.HTTP_200_OK)


# Order API Views
@api_view(['POST'])
def create_order(request):
    user = request.user
    cart = Cart.objects.get(user=user, is_active=True)
    total_amount = sum([item.product.price_retail * item.quantity for item in cart.items.all()])
    order = Order.objects.create(user=user, total_amount=total_amount, status='in_progress')

    for cart_item in cart.items.all():
        OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity,
                                 price=cart_item.product.price_retail)

    cart.is_active = False
    cart.save()

    return Response({'status': 'Order created', 'order_id': order.id}, status=status.HTTP_201_CREATED)


# Favorite API Views
@api_view(['POST', 'DELETE'])
def add_remove_favorite(request):
    user = request.user
    product = Product.objects.get(id=request.data['product_id'])
    if request.method == 'POST':
        Favorite.objects.get_or_create(user=user, product=product)
        return Response({'status': 'Product added to favorites'}, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        favorite = Favorite.objects.get(user=user, product=product)
        favorite.delete()
        return Response({'status': 'Product removed from favorites'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_favorites(request):
    user = request.user
    favorites = Favorite.objects.filter(user=user)
    serializer = FavoriteSerializer(favorites, many=True)
    return Response(serializer.data)


# Supplier Statistics API View
class SupplierStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SupplierStatistics.objects.all()
    serializer_class = SupplierStatisticsSerializer

