from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class StoreSettings(models.Model):
    send_pdf_email = models.BooleanField(default=False, help_text="Automatically send an email with the PDF invoice after checkout.")
    allow_pdf_download = models.BooleanField(default=False, help_text="Show the 'Download Invoice' button on the success page.")
    
    class Meta:
        verbose_name_plural = "Store Settings"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super(StoreSettings, self).save(*args, **kwargs)
        
    def __str__(self):
        return "Store Global Settings"

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    full_description = models.TextField(blank=True, null=True)  
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_gallery/', blank=True, null=True)
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    
    note = models.TextField(blank=True, null=True)
    
    created = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    
    shipping_method = models.CharField(max_length=100, default="Standard")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    payment_method = models.CharField(max_length=100,default="Direct Bank Transfer")
    
    def __str__(self):
        return f"Order {self.id} - {self.first_name} {self.last_name}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"Order {self.order.id} item: {self.product.name}"
    
    def get_total_price(self):
        return self.price * self.quantity
    
    