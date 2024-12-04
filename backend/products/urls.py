from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'supplier-statistics', views.SupplierStatisticsViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/cart/', views.cart_detail, name='cart-detail'),
    path('api/cart/update/<int:cart_item_id>/', views.update_cart_item, name='update-cart-item'),
    path('api/cart/delete/<int:cart_item_id>/', views.delete_cart_item, name='delete-cart-item'),
    path('api/order/create/', views.create_order, name='create-order'),
    path('api/favorites/', views.get_favorites, name='get-favorites'),
    path('api/favorites/add-remove/', views.add_remove_favorite, name='add-remove-favorite'),
]
