import django_filters
from .models import Event

class EventFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    venue = django_filters.CharFilter(field_name='venue', lookup_expr='icontains')
    date = django_filters.DateFilter(field_name='event_date', lookup_expr='date')
    date_from = django_filters.IsoDateTimeFilter(field_name='event_date', lookup_expr='gte')
    date_to = django_filters.IsoDateTimeFilter(field_name='event_date', lookup_expr='lte')
    is_available = django_filters.BooleanFilter(method='filter_is_available')

    class Meta:
        model = Event
        fields = ['name', 'venue', 'vendor', 'date', 'date_from', 'date_to', 'is_available']

    def filter_is_available(self, queryset, name, value):
        if value is True:
            return queryset.filter(available_seats__gt=0)
        elif value is False:
            return queryset.filter(available_seats__lte=0)
        return queryset

