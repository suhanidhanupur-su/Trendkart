from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.conf import settings
from .models import CustomUser, Category, Product
import uuid
import os


# ---------------- HOME ----------------
def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    return render(request, 'base.html', {
        'categories': categories,
        'products': products,
    })


# ---------------- REGISTER ----------------
def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not full_name or not email or not password:
            messages.error(request, 'All fields are required!')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('register')

        base_username = email.split('@')[0]
        unique_username = f"{base_username}_{uuid.uuid4().hex[:6]}"

        CustomUser.objects.create(
            username=unique_username,
            full_name=full_name,
            email=email,
            password=make_password(password)
        )

        messages.success(request, 'Registration successful!')
        return redirect('register')

    return render(request, 'register.html')


# ---------------- CATEGORY ----------------
def category(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})


# ---------------- PRODUCT ----------------
def product(request):
    products = Product.objects.all()
    return render(request, 'product.html', {'products': products})


# ---------------- PRODUCT LIST (optional) ----------------
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

#--------------------------Login_view-------------------
from django.contrib.auth import authenticate, login, logout

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials!")
            return redirect('login')

    return render(request, 'login.html')

# ----------------------Logout_view------------------------------------
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')


def product_detail(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product_detail.html', {'product': product})



def gallery(request):
    return render(request, 'gallery.html')


def about(request):
    return render(request, 'about.html')


def edit_profile(request):
    user = request.user

    if request.method == "POST":
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.full_name = request.POST.get('full_name')
        user.mobile_no = request.POST.get('mobile_no')
        user.address = request.POST.get('address')
        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('edit_profile')

    return render(request, 'edit_profile.html', {'user': user})



def privacy_policy(request):
    return render(request, 'privacy_policy.html')



def refund_policy(request):
    return render(request, 'refund_policy.html')


def shipping_policy(request):
    return render(request, 'shipping_policy.html')



def terms(request):
    return render(request, 'terms.html')



def mission(request):
    return render(request, 'mission.html')


def vision(request):
    return render(request, 'vision.html')



    