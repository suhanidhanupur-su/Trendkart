from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Product
from .models import CustomUser, Category, Product, Cart, Wishlist, OTP, Order, OrderItem


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
admin.site.register(Category)
admin.site.register(Product)



from .models import CustomUser, Category, Product, Cart, Wishlist, OTP, Order, OrderItem, TeamMember, Gallery

admin.site.register(TeamMember)
admin.site.register(Gallery)




from .models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject')

admin.site.register(Contact, ContactAdmin)