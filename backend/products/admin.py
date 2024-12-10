from django.contrib import admin
from .models import (
    Category, Supplier, Product, SupplierPrice, Banner,
    OrderItem, Order, Cart, CartItem, Favorite, Delivery, SupplierStatistics
)

# Inline classes for better admin integration
class SupplierPriceInline(admin.TabularInline):
    model = SupplierPrice
    extra = 1


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


# Custom display for OrderItems within Order
class OrderItemInline(admin.TabularInline):
    model = Order.items.through  # Access the through model for ManyToMany
    extra = 1


# Admin classes for each model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'total_cost', 'status', 'delivery_date', 'payment_method')
    search_fields = ('user_id', 'status')
    list_filter = ('status', 'payment_method', 'delivery_date')
    ordering = ('-timestamp',)
    inlines = [OrderItemInline]  # Updated to use the correct through model


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'supplier', 'quantity', 'unit_price', 'total_price')
    search_fields = ('product__name', 'supplier__name')
    list_filter = ('supplier',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'rating', 'is_favourite')
    search_fields = ('name', 'city')
    list_filter = ('city', 'rating', 'is_favourite')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'article', 'price_retail', 'city', 'min_order_quantity')
    search_fields = ('name', 'article')
    list_filter = ('city', 'price_retail')
    inlines = [SupplierPriceInline]


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('category', 'supplier', 'product', 'photo_preview')

    def photo_preview(self, obj):
        if obj.photo:
            return obj.photo.url
        return "No Image"
    photo_preview.short_description = "Preview"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
    inlines = [CartItemInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'delivery_date', 'status')


@admin.register(SupplierStatistics)
class SupplierStatisticsAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'product', 'total_supplied', 'average_rating', 'last_supply_date')


# Optional: Registering models without custom admin classes
admin.site.register(CartItem)
admin.site.register(SupplierPrice)
