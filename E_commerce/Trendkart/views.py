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




def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')      # ← 'email' name se lega
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password!")
            return redirect('login')

    return render(request, 'login.html')





def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        mobile_no = request.POST.get('mobile_no')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not full_name or not email or not password or not mobile_no or not address:
            messages.error(request, 'Saare fields bharein!')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Passwords match nahi kar rahe!')
            return redirect('register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Yeh email already registered hai!')
            return redirect('register')

        base_username = email.split('@')[0]
        unique_username = f"{base_username}_{uuid.uuid4().hex[:6]}"

        CustomUser.objects.create(
            username=unique_username,
            full_name=full_name,
            email=email,
            mobile_no=mobile_no,
            address=address,
            password=make_password(password)
        )

        messages.success(request, 'Registration successful! Ab login karo.')
        return redirect('login')

    return render(request, 'register.html')





def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    return render(request, 'base.html', {
        'categories': categories,
        'products': products,
        'wishlist_ids': wishlist_ids,
    })



# ------------------register -------------------------------------------

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from .models import CustomUser, Category, Product, Cart, Wishlist, OTP
import random
import uuid

def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        mobile_no = request.POST.get('mobile_no')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check for missing fields
        if not full_name or not email or not password or not mobile_no or not address:
            messages.error(request, 'Please fill in all the fields!')
            return redirect('register')

        # Password match validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

        # Check unique email constraint
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered!')
            return redirect('register')

        # Generate a fallback unique username from email
        base_username = email.split('@')[0]
        unique_username = f"{base_username}_{uuid.uuid4().hex[:6]}"

        # Create user instance as inactive until OTP verification
        user = CustomUser.objects.create(
            username=unique_username,
            full_name=full_name,
            email=email,
            mobile_no=mobile_no,
            address=address,
            password=make_password(password),
            is_active=False  
        )

        # Generate OTP
        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, otp=otp_code)

        # Send Verification Email
        send_mail(
            subject='TrendKart - Email Verification OTP',
            message=f'''
Hello {full_name},

Thank you for choosing TrendKart! To verify your email address and activate your account, please use the following One-Time Password (OTP):

🔐 OTP: {otp_code}

Note: This OTP is valid for 10 minutes. Please do not share this code with anyone.

Best regards,
The TrendKart Team
            ''',
            from_email='suhanidhanupur@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )

        # Cache email into session for tracking verification context
        request.session['verify_email'] = email
        messages.success(request, f'An OTP verification code has been successfully sent to {email}!')
        return redirect('verify_otp')

    return render(request, 'register.html')


# --------------OTP Verify---------------------------------------

def verify_otp(request):
    email = request.session.get('verify_email')

    if not email:
        return redirect('register')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        try:
            user = CustomUser.objects.get(email=email)
            otp_obj = OTP.objects.filter(user=user, is_verified=False).latest('created_at')

            if otp_obj.is_expired():
                messages.error(request, 'OTP expire ho gaya! Dobara register karo.')
                user.delete()
                return redirect('register')

            if otp_obj.otp == entered_otp:
                # OTP sahi hai - user activate karo
                user.is_active = True
                user.save()
                otp_obj.is_verified = True
                otp_obj.save()
                del request.session['verify_email']
                messages.success(request, 'Email verify ho gaya! Ab login karo.')
                return redirect('login')
            else:
                messages.error(request, 'Galat OTP! Dobara try karo.')

        except (CustomUser.DoesNotExist, OTP.DoesNotExist):
            messages.error(request, 'Kuch problem aayi. Dobara register karo.')
            return redirect('register')

    return render(request, 'verify_otp.html', {'email': email})


def resend_otp(request):
    email = request.session.get('verify_email')
    if not email:
        return redirect('register')

    try:
        user = CustomUser.objects.get(email=email)
        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, otp=otp_code)

        send_mail(
            subject='TrendKart - New OTP',
            message=f'Aapka naya OTP: {otp_code}\n\n10 minute mein expire hoga.',
            from_email='suhanidhanupur@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )
        messages.success(request, 'Naya OTP bhej diya gaya!')
    except CustomUser.DoesNotExist:
        return redirect('register')

    return redirect('verify_otp')




from django.db.models import Q

def product(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    selected_category = request.GET.get('category', '')
    max_price = request.GET.get('max_price', '20000')
    search_query = request.GET.get('search', '')
    sort = request.GET.get('sort', '')

    # Category Filter
    if selected_category:
        products = products.filter(category__id=selected_category)

    # Price Filter
    if max_price:
        products = products.filter(product_price__lte=max_price)

    # Search by Product Name + Category Name
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(category__category_name__icontains=search_query)
        )

    # Sorting
    if sort == 'low':
        products = products.order_by('product_price')

    elif sort == 'high':
        products = products.order_by('-product_price')

    # Wishlist
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(
                user=request.user
            ).values_list('product_id', flat=True)
        )

    return render(request, 'product.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'max_price': max_price,
        'search_query': search_query,
        'sort': sort,
        'wishlist_ids': wishlist_ids,
        'search': search_query,
    })