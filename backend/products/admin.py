from django.contrib import admin
from .models import *

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category')
    search_fields = ['name']

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating')
    search_fields = ['name']

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'supplier', 'category', 'price_wholesale', 'price_retail', 'city')
    search_fields = ['name', 'article', 'supplier__name']

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ['cart__user__username', 'product__name']

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ['order__user__username', 'product__name']

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'status', 'total_amount')
    list_filter = ('status',)
    search_fields = ['user__username']

class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'address', 'delivery_date', 'delivery_cost')
    search_fields = ['order__user__username']

class SupplierStatisticsAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'total_orders', 'total_items', 'total_amount')
    search_fields = ['supplier__name']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(SupplierStatistics, SupplierStatisticsAdmin)