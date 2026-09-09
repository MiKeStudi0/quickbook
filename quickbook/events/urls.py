from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet
from bookings.views import BookEventView

router = DefaultRouter()
router.register('', EventViewSet, basename='event')

urlpatterns = [
    path('<int:pk>/book/', BookEventView.as_view(), name='event-book'),
    path('', include(router.urls)),
]
