from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('category/', category, name='category'),
    path('product/', product, name='product'),
]