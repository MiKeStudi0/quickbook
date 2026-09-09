from django.urls import path
from .views import (
    DashboardHomeView,
    StaffLoginView,
    StaffLogoutView,
    VendorListView,
    VendorCreateView,
    VendorUpdateView,
    EventListView,
    EventCreateView,
    EventUpdateView,
    UserListView,
    UserDetailView,
)

urlpatterns = [
    path('', DashboardHomeView.as_view(), name='dashboard-home'),
    path('login/', StaffLoginView.as_view(), name='dashboard-login'),
    path('logout/', StaffLogoutView.as_view(), name='dashboard-logout'),
    path('vendors/', VendorListView.as_view(), name='dashboard-vendor-list'),
    path('vendors/create/', VendorCreateView.as_view(), name='dashboard-vendor-create'),
    path('vendors/<int:pk>/edit/', VendorUpdateView.as_view(), name='dashboard-vendor-update'),
    path('events/', EventListView.as_view(), name='dashboard-event-list'),
    path('events/create/', EventCreateView.as_view(), name='dashboard-event-create'),
    path('events/<int:pk>/edit/', EventUpdateView.as_view(), name='dashboard-event-update'),
    path('users/', UserListView.as_view(), name='dashboard-user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='dashboard-user-detail'),
]
