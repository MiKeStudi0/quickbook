from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    vendor_username = serializers.CharField(source='vendor.username', read_only=True)

    class Meta:
        model = Event
        fields = (
            'id',
            'name',
            'description',
            'venue',
            'event_date',
            'total_seats',
            'available_seats',
            'vendor',
            'vendor_username',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'vendor', 'created_at', 'updated_at')

    def validate(self, data):
        total_seats = data.get('total_seats', getattr(self.instance, 'total_seats', None))
        available_seats = data.get('available_seats', getattr(self.instance, 'available_seats', None))

        if available_seats is not None and total_seats is not None:
            if available_seats > total_seats:
                raise serializers.ValidationError({"available_seats": "Available seats cannot exceed total seats."})

        return data
