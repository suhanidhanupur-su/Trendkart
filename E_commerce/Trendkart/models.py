# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=15)
    dob = models.DateField(null=True, blank=True)
    address = models.TextField()
    alternate_mobile_no = models.CharField(max_length=15, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.email
    

class Category(models.Model):
    category_name = models.CharField(max_length=255)
    category_image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.category_name
    

class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_description = models.TextField()
    product_image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.product_name
    


# -------------------------Cart model-------------------------------------------------
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.product.product_name}"

    def total_price(self):
        return self.product.product_price * self.quantity
    

# ---------------------wishlist-----------------------------------------------------------

class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.product.product_name}"
    

# --------------------OTP-----------------------------------------------
import random
from django.utils import timezone

class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        # OTP 10 minute mein expire ho jayega
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)

    def __str__(self):
        return f"{self.user.email} - {self.otp}"
    

    