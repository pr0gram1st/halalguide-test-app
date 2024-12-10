from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, SupplierViewSet, ProductViewSet, SupplierPriceViewSet,
    BannerViewSet, OrderItemViewSet, OrderViewSet, CartViewSet, FavoriteViewSet, ParentCategoryViewSet,SuppliersByCategoryView, ProductsBySupplierView
)

# Router for all endpoints
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'parent-categories', ParentCategoryViewSet, basename='parent-categories')
router.register(r'suppliers', SupplierViewSet)
router.register(r'products', ProductViewSet)
router.register(r'supplier-prices', SupplierPriceViewSet)
router.register(r'banners', BannerViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'favorites', FavoriteViewSet, basename='favorites')

urlpatterns = [
    path('', include(router.urls)),
    path('suppliers-by-category/', SuppliersByCategoryView.as_view(), name='suppliers-by-category'),
    path('suppliers/<int:supplier_id>/products/', ProductsBySupplierView.as_view(), name='products-by-supplier'),
]
