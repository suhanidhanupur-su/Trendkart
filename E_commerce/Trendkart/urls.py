# Trendkart/urls.py
from .views import *
from django.urls import path
from . import views  # ← Import करो
from .views import verify_otp, resend_otp
from .views import submit_feedback


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('category/', views.category, name='category'),
    path('product/', views.product, name='product'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    path('gallery/', views.gallery, name='gallery'),
    path('about/', views.about, name='about'),

    path('edit-profile/', views.edit_profile, name='edit_profile'),

    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('terms/', views.terms, name='terms'),
    path('mission/', views.mission, name='mission'),
    path('vision/', views.vision, name='vision'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:pk>/', views.update_cart, name='update_cart'),

    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:pk>/', views.toggle_wishlist, name='toggle_wishlist'),


    path('verify-otp/', verify_otp, name='verify_otp'),
    path('resend-otp/', resend_otp, name='resend_otp'),

     path('checkout/', checkout, name='checkout'),
     path('order-confirm/<int:pk>/', order_confirm, name='order_confirm'),
     path('my-orders/', my_orders, name='my_orders'),

     path('forgot-password/', forgot_password, name='forgot_password'),
     path('reset-password-otp/', reset_password_otp, name='reset_password_otp'),
     path('reset-password-new/', reset_password_new, name='reset_password_new'),
     path('contact/', contact, name='contact'),
     
     path('cancel-order/<int:pk>/', views.cancel_order, name='cancel_order'),

     path('feedback/submit/<int:pk>/', submit_feedback, name='submit_feedback'),
     path('inventory/', views.inventory, name='inventory'),
     path('invoice/<int:pk>/', views.download_invoice, name='download_invoice'),
    #  path('feedback/submit/<int:pk>/', submit_feedback, name='submit_feedback'),
    #  path('feedback/list/', feedback_list, name='feedback_list'),
    #  path('feedback/<int:pk>/<str:action>/', feedback_action, name='feedback_action'),
]