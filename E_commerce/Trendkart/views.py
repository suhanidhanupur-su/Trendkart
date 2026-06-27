from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from .models import CustomUser, Category, Product, Cart, Wishlist
import uuid


# ==================== HOME ====================
def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    return render(request, 'base.html', {
        'categories': categories,
        'products': products,
    })


# ==================== REGISTER ====================
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
        return redirect('login')

    return render(request, 'register.html')


# ==================== LOGIN & LOGOUT ====================
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


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')


# ==================== PRODUCT (WITH FILTERS & WISHLIST) ====================
def product(request):
    """Product list with filters, search, sort + wishlist"""
    
    categories = Category.objects.all()
    products = Product.objects.all()

    selected_category = request.GET.get('category', '')
    max_price = request.GET.get('max_price', '20000')
    search_query = request.GET.get('search', '')
    sort = request.GET.get('sort', '')

    if selected_category:
        products = products.filter(category__id=selected_category)
    
    if max_price:
        products = products.filter(product_price__lte=max_price)
    
    if search_query:
        products = products.filter(product_name__icontains=search_query)
    
    if sort == 'low':
        products = products.order_by('product_price')
    elif sort == 'high':
        products = products.order_by('-product_price')

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    return render(request, 'product.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category or '',
        'max_price': max_price or '20000',
        'search_query': search_query or '',
        'sort': sort or '',
        'wishlist_ids': wishlist_ids,
    })


# ==================== PRODUCT DETAIL ====================
def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()
    
    return render(request, 'product_detail.html', {
        'product': product,
        'is_wishlisted': is_wishlisted,
    })


# ==================== CART VIEWS ====================
@login_required(login_url='login')
def add_to_cart(request, pk):
    product = get_object_or_404(Product, id=pk)
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f'"{product.product_name}" added to cart!')
    return redirect('cart')


@login_required(login_url='login')
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total,
    })


@login_required(login_url='login')
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(Cart, id=pk, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('cart')


@login_required(login_url='login')
def update_cart(request, pk):
    cart_item = get_object_or_404(Cart, id=pk, user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


# ==================== WISHLIST VIEWS ====================
@login_required(login_url='login')
def toggle_wishlist(request, pk):
    """Add/Remove product from wishlist"""
    product = get_object_or_404(Product, id=pk)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)

    if wishlist_item.exists():
        wishlist_item.delete()
        messages.success(request, f'"{product.product_name}" removed from wishlist!')
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, f'"{product.product_name}" added to wishlist!')

    return redirect(request.META.get('HTTP_REFERER', 'product'))


@login_required(login_url='login')
def wishlist_view(request):
    """Display user's wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})


# ==================== CATEGORY ====================
def category(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})


# ==================== OTHER PAGES ====================
@login_required(login_url='login')
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        user.full_name = request.POST.get('full_name', '')
        user.email = request.POST.get('email', '')
        user.mobile_no = request.POST.get('mobile_no', '')
        user.alternate_mobile_no = request.POST.get('alternate_mobile_no', '')
        user.address = request.POST.get('address', '')
        user.dob = request.POST.get('dob') or None
        user.gender = request.POST.get('gender', '')

        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES['profile_image']

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('edit_profile')

    return render(request, 'edit_profile.html', {'user': user})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


def gallery(request):
    return render(request, 'gallery.html')


def about(request):
    return render(request, 'about.html')


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