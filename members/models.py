from django.db import models


# Create your models here.
class Category(models.Model):
    """Fish categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default='🐟')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Categories"


class customer_sign(models.Model):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('seller', 'Seller'),
    )
    
    ROLE_CHOICES = (
        ('superadmin', 'SuperAdmin'),
        ('admin', 'Admin'),
        ('user', 'User'),
        ('moderator', 'Moderator'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')  # Added role field
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)  # For seller approval
    is_blocked = models.BooleanField(default=False)  # For blocking fake users
    date_created = models.DateTimeField(auto_now_add=True)
    
    # Location fields for sellers
    area = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()} - {self.get_role_display()})"
    
    class Meta:
        ordering = ['-date_created']


class Fish(models.Model):
    """Fish products listing by sellers"""
    seller = models.ForeignKey(customer_sign, on_delete=models.CASCADE, related_name='fish_products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_kg = models.FloatField()
    image = models.ImageField(upload_to='fish_images/')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.seller.username}"
    
    class Meta:
        ordering = ['-created_at']


class Order(models.Model):
    """Orders placed by customers"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    seller = models.ForeignKey(customer_sign, on_delete=models.CASCADE, related_name='seller_orders')
    customer = models.ForeignKey(customer_sign, on_delete=models.CASCADE, related_name='customer_orders', null=True, blank=True)
    fish = models.ForeignKey(Fish, on_delete=models.CASCADE, related_name='orders')
    quantity_kg = models.FloatField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Delivery Location Fields
    delivery_state = models.CharField(max_length=100, blank=True, null=True)
    delivery_city = models.CharField(max_length=100, blank=True, null=True)
    delivery_district = models.CharField(max_length=100, blank=True, null=True)
    delivery_village = models.CharField(max_length=100, blank=True, null=True)
    
    # Payment Info
    payment_method = models.CharField(max_length=50, blank=True, null=True, default='cash_on_delivery')
    commission_5_percent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_commission(self):
        """Calculate 5% commission on total price"""
        commission = (self.total_price * 5) / 100
        self.commission_5_percent = commission
        return commission
    
    def get_seller_amount(self):
        """Get amount seller receives after 5% commission"""
        return self.total_price - self.commission_5_percent

    def __str__(self):
        return f"Order #{self.id} - {self.fish.name} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']


class AboutMessage(models.Model):
    """Contact messages from users"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Contact Messages"


