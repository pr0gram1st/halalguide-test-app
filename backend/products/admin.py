from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Supplier, Product, SupplierPrice, Banner,
    Order, Cart, CartItem, Favorite, Delivery, Application
)

# Inline classes
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


class SupplierPriceInline(admin.TabularInline):
    model = SupplierPrice
    extra = 1
    fields = ['supplier', 'price']


# Admin classes
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'city', 'rating', 'is_favourite',
        'price_wholesale', 'price_retail', 'min_order_quantity',
        'delivery_time'
    )
    search_fields = ('name', 'city')
    list_filter = ('city', 'rating', 'is_favourite')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'article', 'city', 'description', 'is_favorite', 'get_suppliers')
    search_fields = ('name', 'article', 'city', 'description')
    list_filter = ('city', 'is_favorite')
    fieldsets = (
        (None, {'fields': ('name', 'article')}),
        ('Product Details', {'fields': ('city', 'description', 'characteristics', 'photo', 'category')}),
        ('Favorites', {'fields': ('is_favorite',)}),
    )
    inlines = [SupplierPriceInline]

    def get_suppliers(self, obj):
        return ", ".join([str(sp.supplier.name) for sp in obj.supplierprice_set.all()])
    get_suppliers.short_description = 'Suppliers'


@admin.register(SupplierPrice)
class SupplierPriceAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'product', 'price', 'delivery_time')
    search_fields = ('supplier__name', 'product__name')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('category', 'supplier', 'product', 'photo_preview')

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.photo.url)
        return "No Image"
    photo_preview.short_description = "Preview"


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
    list_display = ('id', 'user', 'product', 'supplier')
    search_fields = ('user__username', 'product__name', 'supplier__name')


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'contact_number', 'delivery_date', 'status', 'created_at')
    search_fields = ('user__username', 'address')
    list_filter = ('status', 'delivery_date')
