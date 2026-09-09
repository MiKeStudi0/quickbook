import time
from django.db import transaction, OperationalError
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from events.models import Event
from .models import Booking
from .serializers import BookingSerializer, CreateBookingSerializer

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class BookEventView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateBookingSerializer

    @extend_schema(
        tags=["Bookings"],
        summary="Book seats for an event",
        request=CreateBookingSerializer,
        responses={201: BookingSerializer, 400: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}
    )
    def post(self, request, pk):
        serializer = CreateBookingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        quantity = serializer.validated_data.get('quantity', 1)

        max_retries = 5
        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    try:
                        event = Event.objects.select_for_update().get(pk=pk)
                    except Event.DoesNotExist:
                        return Response({"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

                    if event.available_seats < quantity:
                        return Response({"detail": "Not enough seats available."}, status=status.HTTP_400_BAD_REQUEST)

                    event.available_seats -= quantity
                    event.save(update_fields=["available_seats"])

                    booking = Booking.objects.create(
                        user=request.user,
                        event=event,
                        quantity=quantity,
                        status=Booking.Status.CONFIRMED,
                    )

                    booking_data = BookingSerializer(booking).data
                    return Response(booking_data, status=status.HTTP_201_CREATED)
            except OperationalError:
                if attempt == max_retries - 1:
                    return Response({"detail": "System busy processing another booking, please try again."}, status=status.HTTP_400_BAD_REQUEST)
                time.sleep(0.05 * (attempt + 1))


class CancelBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookingSerializer

    @extend_schema(
        tags=["Bookings"],
        summary="Cancel an existing booking",
        request=None,
        responses={200: BookingSerializer, 400: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}
    )
    def post(self, request, pk):
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    try:
                        booking = Booking.objects.select_for_update().get(pk=pk)
                    except Booking.DoesNotExist:
                        return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

                    if booking.user != request.user and not request.user.is_staff:
                        return Response({"detail": "You do not have permission to cancel this booking."}, status=status.HTTP_403_FORBIDDEN)

                    if booking.status == Booking.Status.CANCELLED:
                        return Response({"detail": "Booking is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)

                    event = Event.objects.select_for_update().get(pk=booking.event_id)
                    event.available_seats += booking.quantity
                    if event.available_seats > event.total_seats:
                        event.available_seats = event.total_seats
                    event.save(update_fields=["available_seats"])

                    booking.status = Booking.Status.CANCELLED
                    booking.cancelled_at = timezone.now()
                    booking.save(update_fields=["status", "cancelled_at"])

                    return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)
            except OperationalError:
                if attempt == max_retries - 1:
                    return Response({"detail": "System busy, please try again."}, status=status.HTTP_400_BAD_REQUEST)
                time.sleep(0.05 * (attempt + 1))


class BookingHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = BookingSerializer

    @extend_schema(
        tags=["Bookings"],
        summary="List user or system booking history",
        parameters=[
            OpenApiParameter(name='status', type=OpenApiTypes.STR, description='Filter by status (CONFIRMED or CANCELLED)', required=False),
            OpenApiParameter(name='page', type=OpenApiTypes.INT, description='Page number', required=False),
            OpenApiParameter(name='page_size', type=OpenApiTypes.INT, description='Number of results per page', required=False),
        ],
        responses={200: BookingSerializer(many=True)}
    )
    def get(self, request):
        queryset = Booking.objects.select_related('user', 'event').all()

        if not request.user.is_staff:
            queryset = queryset.filter(user=request.user)

        booking_status = request.query_params.get('status')
        if booking_status:
            queryset = queryset.filter(status__iexact=booking_status)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = BookingSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = BookingSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
