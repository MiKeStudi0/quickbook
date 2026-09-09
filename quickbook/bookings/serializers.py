from rest_framework import serializers
from .models import Booking
from events.serializers import EventSerializer

class BookingSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    event_detail = EventSerializer(source='event', read_only=True)

    class Meta:
        model = Booking
        fields = (
            'id',
            'user',
            'user_username',
            'event',
            'event_detail',
            'quantity',
            'status',
            'created_at',
            'cancelled_at',
        )
        read_only_fields = ('id', 'user', 'event', 'status', 'created_at', 'cancelled_at')


class CreateBookingSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(default=1, min_value=1)
