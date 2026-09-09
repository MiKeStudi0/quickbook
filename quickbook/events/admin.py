from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'venue', 'event_date', 'total_seats', 'available_seats', 'vendor', 'created_at')
    list_filter = ('event_date', 'venue', 'vendor')
    search_fields = ('name', 'description', 'venue')
