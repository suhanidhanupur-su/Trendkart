from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.conf import settings
from .models import CustomUser
import uuid
import os

def home(request):
    banner_images = []
    banner_dir = os.path.join(settings.BASE_DIR, 'Static', 'images')
    if os.path.isdir(banner_dir):
        for filename in sorted(os.listdir(banner_dir)):
            if filename.lower().startswith('banner') and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                banner_images.append(f'images/{filename}')

    return render(request, 'base.html', {
        'banner_images': banner_images
    })

def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Basic validations
        if not full_name or not email or not password:
            messages.error(request, 'All fields are required!')
            return redirect('register')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long!')
            return redirect('register')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered!')
            return redirect('register')

        # Create user
        # Since username is required by AbstractUser but we want to use email, 
        # we can generate a random username or use part of the email.
        base_username = email.split('@')[0]
        unique_username = f"{base_username}_{uuid.uuid4().hex[:6]}"

        try:
            user = CustomUser.objects.create(
                username=unique_username,
                full_name=full_name,
                email=email,
                password=make_password(password)
            )
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('register')
        except Exception as e:
            messages.error(request, 'An error occurred during registration. Please try again.')
            return redirect('register')

    return render(request, 'register.html')

from .models import Category, Product


def category(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {
        'categories': categories
    })


def product(request):
    products = Product.objects.all()
    return render(request, 'product.html', {
        'products': products
    })