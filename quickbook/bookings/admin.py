from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'event', 'quantity', 'status', 'created_at', 'cancelled_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'event__name')
