from django.contrib import admin
from .models import customer_sign, Fish, Order, Category
from django.contrib import messages
from django.contrib import messages


# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)


@admin.register(customer_sign)
class CustomerSignAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'role', 'is_active', 'is_blocked', 'is_verified', 'date_created')
    list_filter = ('user_type', 'role', 'is_active', 'is_blocked', 'is_verified', 'date_created', 'state')
    search_fields = ('username', 'email', 'mobile_number', 'area', 'district', 'state')
    readonly_fields = ('date_created',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('username', 'email', 'mobile_number')
        }),
        ('Account Type', {
            'fields': ('user_type', 'role')
        }),
        ('Security & Status', {
            'fields': ('password', 'is_active', 'is_blocked', 'is_verified')
        }),
        ('Location Information', {
            'fields': ('area', 'district', 'state', 'latitude', 'longitude'),
            'classes': ('collapse',),
            'description': 'Location data for sellers'
        }),
        ('Timestamps', {
            'fields': ('date_created',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Superadmin can edit everything, others have restrictions
        if request.user.is_superuser:
            return ('date_created',)
        return ('date_created', 'user_type', 'role', 'is_active')


@admin.register(Fish)
class FishAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'category', 'price', 'available_kg', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'seller', 'category')
    search_fields = ('name', 'seller__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Fish Information', {
            'fields': ('seller', 'category', 'name', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'available_kg')
        }),
        ('Image', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'fish', 'seller', 'customer_name', 'quantity_kg', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'seller')
    search_fields = ('customer_name', 'customer_email', 'fish__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('seller', 'fish', 'quantity_kg', 'total_price')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
