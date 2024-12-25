from django.contrib import admin
from .models import (
    Category, Supplier, Product, SupplierPrice, Banner,
    Order, Cart, CartItem, Favorite, Delivery, Application
)

# Inline classes
class SupplierPriceInline(admin.TabularInline):
    model = SupplierPrice
    extra = 1


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


# Admin classes
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'rating', 'is_favourite')
    search_fields = ('name', 'city')
    list_filter = ('city', 'rating', 'is_favourite')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'article', 'price_retail', 'city', 'min_order_quantity', 'is_favorite')
    search_fields = ('name', 'article')
    list_filter = ('city', 'price_retail')
    inlines = [SupplierPriceInline]


@admin.register(SupplierPrice)
class SupplierPriceAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'product', 'price', 'delivery_time')
    search_fields = ('supplier__name', 'product__name')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('category', 'supplier', 'product', 'photo_preview')

    def photo_preview(self, obj):
        if obj.photo:
            return f'<img src="{obj.photo.url}" style="width: 50px; height: 50px;" />'
        return "No Image"
    photo_preview.short_description = "Preview"
    photo_preview.allow_tags = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier_details', 'product', 'quantity', 'total_cost')
    search_fields = ('supplier_details__name', 'product__name')
    ordering = ('-id',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'payment_method', 'delivery_date', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('status', 'payment_method', 'created_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'supplier')
    search_fields = ('user__username', 'product__name', 'supplier__name')


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'contact_number', 'delivery_date', 'status', 'created_at')
    search_fields = ('user__username', 'address')
    list_filter = ('status', 'delivery_date')


# Removing unnecessary `admin.site.register` calls since all models are explicitly handled.
