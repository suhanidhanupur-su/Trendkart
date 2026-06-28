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
    


# ------------------------Order models--------------------------------------
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    PAYMENT_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('Online', 'Online Payment'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='COD')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.product_name} x {self.quantity}"

    def subtotal(self):
        return self.price * self.quantity
    



class TeamMember(models.Model):
    employee_image = models.ImageField(upload_to='team/', null=True, blank=True)
    employee_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.employee_name


class Gallery(models.Model):
    image = models.ImageField(upload_to='gallery/')
    title = models.CharField(max_length=255, null=True, blank=True)
    caption = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title or "Gallery Image"
    


# --------------------contact us-------------------------------
class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"    

# ------------------------orderitem------------------
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

# -------------------------------status-------------------
STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Confirmed', 'Confirmed'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
)

status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default='Pending'
)