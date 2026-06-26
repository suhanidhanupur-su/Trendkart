from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('category/', category, name='category'),
    path('product/', product, name='product'),
    path('product/<int:pk>/', product_detail, name='product_detail'),

    path('gallery/', gallery, name='gallery'),
    path('about/', about, name='about'),

    path('edit-profile/', edit_profile, name='edit_profile'),

    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('refund-policy/', refund_policy, name='refund_policy'),
    path('shipping-policy/', shipping_policy, name='shipping_policy'),
    path('terms/', terms, name='terms'),
    path('mission/', mission, name='mission'),
    path('vision/', vision, name='vision'),
]