from django.contrib import admin
from .models import Category, Product, ProductImage, Order, OrderItem, StoreSettings, UserProfile

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    inlines = [ProductImageInline]
    
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'created', 'paid')
    list_filter = ('paid', 'created')
    inlines = [OrderItemInline] 
    

admin.site.register(StoreSettings)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(UserProfile)