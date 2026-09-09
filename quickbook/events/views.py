from rest_framework import viewsets, filters, permissions
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event
from .serializers import EventSerializer
from .filters import EventFilter

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().select_related('vendor').order_by('-created_at')
    serializer_class = EventSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['name', 'description', 'venue']
    ordering_fields = ['event_date', 'created_at', 'name', 'available_seats']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Assign current authenticated user as vendor if not explicitly provided
        serializer.save(vendor=self.request.user)
