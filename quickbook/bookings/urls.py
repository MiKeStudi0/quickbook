from django.urls import path
from .views import BookEventView, CancelBookingView, BookingHistoryView

urlpatterns = [
    path('', BookingHistoryView.as_view(), name='booking-history'),
    path('<int:pk>/cancel/', CancelBookingView.as_view(), name='booking-cancel'),
    path('book/<int:pk>/', BookEventView.as_view(), name='booking-create-alt'),
]
