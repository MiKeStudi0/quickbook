from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'is_vendor', 'is_staff', 'referral_code', 'referred_by', 'created_at')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('is_vendor', 'referral_code', 'referred_by')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Fields', {'fields': ('is_vendor', 'referral_code', 'referred_by')}),
    )
