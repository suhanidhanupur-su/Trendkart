from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Product, Cart, Wishlist, OTP, Order, OrderItem, TeamMember, Gallery, Contact

# 1. Custom User Admin Configuration
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Custom Profile Details', {
            'fields': (
                'email',
                'full_name',
                'mobile_no',
                'alternate_mobile_no',
                'dob',
                'address',
                'profile_image',
                'gender'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Profile Details', {
            'fields': (
                'full_name',
                'email',
                'mobile_no',
                'alternate_mobile_no',
                'dob',
                'address',
                'profile_image',
                'gender'
            )
        }),
    )

    list_display = (
        'username',
        'email',
        'full_name',
        'mobile_no',
        'is_staff'
    )

admin.site.register(CustomUser, CustomUserAdmin)

# 2. Product Admin Configuration (With SKU and Stock)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'product_price', 'sku', 'stock'] 
    list_editable = ['product_price', 'stock'] 
    search_fields = ['product_name', 'sku']

# 3. Order Admin Configuration
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'total_amount', 'status', 'created_at']
    list_editable = ['status']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'full_name', 'user__email']

# 4. Contact Admin Configuration
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject')

admin.site.register(Contact, ContactAdmin)

# 5. Remaining Models Registration
admin.site.register(Category)
admin.site.register(TeamMember)
admin.site.register(Gallery)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(OTP)
admin.site.register(OrderItem)