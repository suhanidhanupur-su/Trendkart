import uuid
import random
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db.models import Q
from .models import (
    CustomUser, Category, Product, Cart, Wishlist,
    OTP, Order, OrderItem, TeamMember,
    Gallery, Contact, Feedback
)

# ==================== HOME ====================
def home(request):
    """Displays homepage with categories, products, and wishlist tracking."""
    categories = Category.objects.all()
    products = Product.objects.all()

    # Low Stock Alert Logic (Stock less than 5)
    low_stock_alerts = Product.objects.filter(stock__lt=5)

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    return render(request, 'base.html', {
        'categories': categories,
        'products': products,
        'wishlist_ids': wishlist_ids,
        'low_stock_alerts': low_stock_alerts,
    })


# ==================== AUTHENTICATION (REGISTER, LOGIN, LOGOUT) ====================
def register(request):
    """Handles user registration and sends an OTP email verification code."""
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        mobile_no = request.POST.get('mobile_no')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not full_name or not email or not password or not mobile_no or not address:
            messages.error(request, 'Please fill in all fields!')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered!')
            return redirect('register')

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

        request.session['verify_email'] = email
        messages.success(request, f'An OTP verification code has been successfully sent to {email}!')
        return redirect('verify_otp')

    return render(request, 'register.html')


def login_view(request):
    """Authenticates the user using email and password."""
    if request.method == "POST":
        email = request.POST.get('email')
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


def logout_view(request):
    """Logs out the active user session."""
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')


# ==================== OTP VERIFICATION ====================
def verify_otp(request):
    """Verifies the registration OTP code and activates the account."""
    email = request.session.get('verify_email')

    if not email:
        return redirect('register')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        try:
            user = CustomUser.objects.get(email=email)
            otp_obj = OTP.objects.filter(user=user, is_verified=False).latest('created_at')

            if otp_obj.is_expired():
                messages.error(request, 'OTP expired! Please register again.')
                user.delete()
                return redirect('register')

            if otp_obj.otp == entered_otp:
                user.is_active = True
                user.save()
                otp_obj.is_verified = True
                otp_obj.save()
                del request.session['verify_email']
                messages.success(request, 'Email verified successfully! You can now log in.')
                return redirect('login')
            else:
                messages.error(request, 'Incorrect OTP! Please try again.')

        except (CustomUser.DoesNotExist, OTP.DoesNotExist):
            messages.error(request, 'An error occurred. Please register again.')
            return redirect('register')

    return render(request, 'verify_otp.html', {'email': email})


def resend_otp(request):
    """Resends a new verification OTP code to the registration email."""
    email = request.session.get('verify_email')
    if not email:
        return redirect('register')

    try:
        user = CustomUser.objects.get(email=email)
        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, otp=otp_code)

        send_mail(
            subject='TrendKart - New OTP',
            message=f'Your new OTP is: {otp_code}\n\nIt expires in 10 minutes.',
            from_email='suhanidhanupur@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )
        messages.success(request, 'A new OTP has been sent!')
    except CustomUser.DoesNotExist:
        return redirect('register')

    return redirect('verify_otp')


# ==================== PASSWORD RESET (FORGOT PASSWORD) ====================
def forgot_password(request):
    """Handles password reset entry and emails a verification OTP."""
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = CustomUser.objects.get(email=email)
            otp_code = str(random.randint(100000, 999999))
            OTP.objects.create(user=user, otp=otp_code)

            send_mail(
                subject='TrendKart - Password Reset OTP',
                message=f'''
Hello {user.full_name}!

Your OTP to reset your password is:

🔐 OTP: {otp_code}

This OTP is valid for 10 minutes.
If you did not request this, please ignore this email.

TrendKart Team
                ''',
                from_email='suhanidhanupur@gmail.com',
                recipient_list=[email],
                fail_silently=False,
            )

            request.session['reset_email'] = email
            messages.success(request, f'OTP has been sent to {email}!')
            return redirect('reset_password_otp')

        except CustomUser.DoesNotExist:
            messages.error(request, 'This email is not registered!')
            return redirect('forgot_password')

    return render(request, 'forgot_password.html')


def reset_password_otp(request):
    """Verifies the password reset OTP code."""
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        try:
            user = CustomUser.objects.get(email=email)
            otp_obj = OTP.objects.filter(user=user, is_verified=False).latest('created_at')

            if otp_obj.is_expired():
                messages.error(request, 'OTP expired! Please try again.')
                return redirect('forgot_password')

            if otp_obj.otp == entered_otp:
                otp_obj.is_verified = True
                otp_obj.save()
                request.session['reset_verified'] = True
                return redirect('reset_password_new')
            else:
                messages.error(request, 'Incorrect OTP! Please try again.')

        except (CustomUser.DoesNotExist, OTP.DoesNotExist):
            messages.error(request, 'An error occurred. Please try again.')
            return redirect('forgot_password')

    return render(request, 'reset_password_otp.html', {'email': email})


def reset_password_new(request):
    """Saves the new password updated by the user."""
    email = request.session.get('reset_email')
    verified = request.session.get('reset_verified')

    if not email or not verified:
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('reset_password_new')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long!')
            return redirect('reset_password_new')

        try:
            user = CustomUser.objects.get(email=email)
            user.password = make_password(password)
            user.save()

            del request.session['reset_email']
            del request.session['reset_verified']

            messages.success(request, 'Password reset successfully! You can now log in.')
            return redirect('login')

        except CustomUser.DoesNotExist:
            return redirect('forgot_password')

    return render(request, 'reset_password_new.html')


# ==================== PRODUCTS & FILTERING ====================
def product(request):
    """Lists products with advanced searching, categorization, pricing limits, and sorting."""
    categories = Category.objects.all()
    products = Product.objects.all()

    selected_category = request.GET.get('category', '')
    max_price = request.GET.get('max_price', '20000')
    search_query = request.GET.get('search', '')  # Matches name="search" from base.html
    sort = request.GET.get('sort', '')

    if selected_category:
        products = products.filter(category__id=selected_category)

    if max_price:
        products = products.filter(product_price__lte=max_price)

    if search_query:
        # Search by Product Name, Category Name, or SKU
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(category__category_name__icontains=search_query) |
            Q(sku__icontains=search_query)
        )

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
        'selected_category': selected_category,
        'max_price': max_price,
        'search_query': search_query,
        'sort': sort,
        'wishlist_ids': wishlist_ids,
        'search': search_query,
    })


def product_detail(request, pk):
    """Detailed view for a selected product, checking wishlist status."""
    product = get_object_or_404(Product, id=pk)
    
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()
    
    return render(request, 'product_detail.html', {
        'product': product,
        'is_wishlisted': is_wishlisted,
    })


def category(request):
    """Lists all available product categories."""
    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})


def product_list(request):
    """Standard fallback catalog listing."""
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


# ==================== SHOPPING CART ====================
@login_required(login_url='login')
def add_to_cart(request, pk):
    """Adds a item or increments its current quantity inside user's shopping cart."""
    product = get_object_or_404(Product, id=pk)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f'"{product.product_name}" added to cart!')
    return redirect('cart')


@login_required(login_url='login')
def cart_view(request):
    """Displays items present inside user's shopping cart along with total calculations."""
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total,
    })


@login_required(login_url='login')
def remove_from_cart(request, pk):
    """Removes a specific product match directly from user's shopping cart."""
    cart_item = get_object_or_404(Cart, id=pk, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('cart')


@login_required(login_url='login')
def update_cart(request, pk):
    """Updates selected numeric configurations for target cart quantities."""
    cart_item = get_object_or_404(Cart, id=pk, user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


# ==================== WISHLIST ====================
@login_required(login_url='login')
def toggle_wishlist(request, pk):
    """Toggles item retention state inside active wishlist registers."""
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
    """Displays saved products present inside user's personal wishlist."""
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})


# ==================== CHECKOUT & ORDERING (WITH RAZORPAY) ====================
@login_required(login_url='login')
def checkout(request):
    """Processes user details and compiles structured invoices to secure active shopping orders."""
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items:
        messages.error(request, 'Cart khali hai!')
        return redirect('cart')

    total = sum(item.total_price() for item in cart_items)
    razorpay_order_id = ""

    # Razorpay client initialize karo
    client = razorpay.Client(
        auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET)
    )

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        payment_verified = False  

        if payment_method == 'Online':
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')

            if not payment_id or not order_id or not signature:
                messages.error(request, 'Payment incomplete ya cancel ho gayi thi!')
                return redirect('checkout')

            try:
                params = {
                    'razorpay_order_id': order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': signature
                }
                client.utility.verify_payment_signature(params)
                payment_verified = True
            except razorpay.errors.SignatureVerificationError:
                messages.error(request, 'Payment verification failed!')
                return redirect('checkout')
            except Exception as e:
                print(f"Payment error: {e}")  
                messages.error(request, f'Payment error: {str(e)}')
                return redirect('checkout')
        else:
            payment_verified = True

        if payment_verified:
            full_name = request.POST.get('full_name')
            mobile = request.POST.get('mobile')
            address = request.POST.get('address')
            city = request.POST.get('city')
            pincode = request.POST.get('pincode')

            order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                mobile=mobile,
                address=address,
                city=city,
                pincode=pincode,
                payment_method=payment_method,
                total_amount=total,
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.product_price,
                )

            cart_items.delete()
            messages.success(request, 'Order placed successfully!')
            return redirect('order_confirm', pk=order.id)

    else:
        try:
            razorpay_order = client.order.create({
                'amount': int(total * 100),
                'currency': 'INR',
                'payment_capture': 1
            })
            razorpay_order_id = razorpay_order['id']
        except Exception as e:
            messages.error(request, 'Razorpay configuration error!')
            
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'user': request.user,
        'razorpay_key': settings.RAZORPAY_API_KEY,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_amount': int(total * 100),
    })


@login_required(login_url='login')
def order_confirm(request, pk):
    """Displays order success summary information details."""
    order = get_object_or_404(Order, id=pk, user=request.user)
    return render(request, 'order_confirm.html', {'order': order})


@login_required(login_url='login')
def my_orders(request):
    """Lists current purchase history summaries related to the authenticated user account."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})


# ==================== OTHER CORE & STATIC PAGES ====================
@login_required(login_url='login')
def edit_profile(request):
    """Allows profile modifications and updating structural user parameters."""
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


def about(request):
    """Renders basic information regarding corporate infrastructure profile descriptions."""
    team_members = TeamMember.objects.all()
    return render(request, 'about.html', {'team_members': team_members})


def gallery(request):
    """Displays dynamic image albums."""
    images = Gallery.objects.all()
    return render(request, 'gallery.html', {'images': images})


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


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if not name or not email or not message:
            messages.error(request, 'Please fill all required fields!')
            return redirect('contact')

        Contact.objects.create(
            name=name,
            email=email,
            mobile=mobile,
            subject=subject,
            message=message,
        )

        send_mail(
            subject=f'TrendKart Contact: {subject}',
            message=f'Name: {name}\nEmail: {email}\nMobile: {mobile}\n\nMessage:\n{message}',
            from_email='suhanidhanupur@gmail.com',
            recipient_list=['suhanidhanupur@gmail.com'],
            fail_silently=True,
        )

        messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
        return redirect('contact')

    return render(request, 'contact.html')


@login_required(login_url='login')
def cancel_order(request, pk):
    order = get_object_or_404(Order, id=pk, user=request.user)

    if order.status in ['Pending', 'Confirmed']:
        order.status = 'Cancelled'
        order.save()
        messages.success(request, 'Order cancelled successfully!')
    else:
        messages.error(request, 'This order cannot be cancelled.')

    return redirect('my_orders')






@login_required(login_url='login')
def submit_feedback(request, pk):
    return redirect('product_detail', pk=pk)


@login_required(login_url='login')
def feedback_list(request):
    return render(request, 'feedback_list.html')


@login_required(login_url='login')
def feedback_action(request, pk, action):
    return redirect('feedback_list')


@login_required(login_url='login')
def submit_feedback(request, pk):
    product = get_object_or_404(Product, id=pk)

    if request.method == 'POST':
        message = request.POST.get('message')
        rating = request.POST.get('rating', 5)

        already_reviewed = Feedback.objects.filter(
            user=request.user,
            product=product
        ).exists()

        if already_reviewed:
            messages.error(request, 'You already reviewed this product!')
        else:
            Feedback.objects.create(
                user=request.user,
                product=product,
                message=message,
                rating=rating
            )
            messages.success(request, 'Review submitted successfully!')

    return redirect('product_detail', pk=pk)


@login_required(login_url='login')
def feedback_list(request):
    if not request.user.is_staff:
        return redirect('home')

    feedbacks = Feedback.objects.all().order_by('-created_at')

    return render(request, 'feedback_list.html', {
        'feedbacks': feedbacks
    })


@login_required(login_url='login')
def feedback_action(request, pk, action):
    if not request.user.is_staff:
        return redirect('home')

    feedback = get_object_or_404(Feedback, id=pk)

    if action == 'approve':
        feedback.status = 'Approved'
        feedback.save()

    elif action == 'reject':
        feedback.status = 'Rejected'
        feedback.save()

    return redirect('feedback_list')




from .models import Feedback, Product

@login_required(login_url='login')
def submit_feedback(request, pk):
    product = get_object_or_404(Product, id=pk)

    if request.method == "POST":
        rating = request.POST.get('rating')
        message = request.POST.get('message')

        Feedback.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            message=message,
            status='Pending'
        )

        messages.success(request, "Review submitted successfully!")
    
    return redirect('product_detail', pk=pk)


# Inventory 
@login_required(login_url='login')
def inventory(request):
    products = Product.objects.all()

    return render(request, 'inventory.html', {
        'products': products
    })