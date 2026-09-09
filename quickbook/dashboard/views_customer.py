from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, DatabaseError
from django.db.models import Q
import time

from events.models import Event
from bookings.models import Booking
from referrals.services import get_or_create_referral_node, build_tree_dict, get_team_stats
from .forms import StaffLoginForm

User = get_user_model()


class CustomerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/customer/login/'

    def test_func(self):
        return self.request.user.is_authenticated and not self.request.user.is_staff and not self.request.user.is_vendor

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return redirect('dashboard-home')
            elif self.request.user.is_vendor:
                return redirect('dashboard-event-list')
        return redirect('customer-login')


class CustomerLoginView(LoginView):
    template_name = 'customer/login.html'
    authentication_form = StaffLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if user.is_staff or user.is_vendor:
            form.add_error(None, "Staff and Vendor accounts must sign in via the Staff/Vendor Portal (/dashboard/login/).")
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('customer-events')


class CustomerLogoutView(LogoutView):
    next_page = reverse_lazy('customer-login')


class CustomerEventListView(CustomerRequiredMixin, ListView):
    model = Event
    template_name = 'customer/events.html'
    context_object_name = 'events'
    paginate_by = 6

    def get_template_names(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or self.request.GET.get('ajax') == '1':
            return ['customer/partials/events_grid.html']
        return [self.template_name]

    def get_queryset(self):
        qs = Event.objects.filter(available_seats__gt=0).select_related('vendor').order_by('event_date')
        
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(venue__icontains=query) | Q(description__icontains=query))
            
        date_param = self.request.GET.get('date')
        if date_param:
            qs = qs.filter(event_date__date=date_param)

        vendor_param = self.request.GET.get('vendor')
        if vendor_param and vendor_param.isdigit():
            qs = qs.filter(vendor_id=int(vendor_param))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendors'] = User.objects.filter(is_vendor=True)
        params = self.request.GET.copy()
        if 'page' in params:
            del params['page']
        context['querystring'] = params.urlencode()
        return context




class CustomerBookEventView(CustomerRequiredMixin, View):
    def post(self, request, pk):
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            messages.error(request, "Please enter a valid ticket quantity.")
            return redirect('customer-events')

        max_retries = 3
        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    event = Event.objects.select_for_update().get(pk=pk)

                    if event.available_seats < quantity:
                        messages.error(request, f"Insufficient seats available! Only {event.available_seats} remaining.")
                        return redirect('customer-events')

                    event.available_seats -= quantity
                    event.save(update_fields=['available_seats'])

                    Booking.objects.create(
                        user=request.user,
                        event=event,
                        quantity=quantity,
                        status=Booking.Status.CONFIRMED
                    )

                    messages.success(request, f"Successfully booked {quantity} ticket(s) for '{event.name}'!")
                    return redirect('customer-bookings')
            except DatabaseError:
                if attempt == max_retries - 1:
                    messages.error(request, "Server busy processing concurrent bookings. Please try again.")
                    return redirect('customer-events')
                time.sleep(0.05 * (2 ** attempt))

        return redirect('customer-events')


class CustomerBookingListView(CustomerRequiredMixin, ListView):
    model = Booking
    template_name = 'customer/bookings.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related('event').order_by('-created_at')


class CustomerCancelBookingView(CustomerRequiredMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, user=request.user)

        if booking.status == Booking.Status.CANCELLED:
            messages.info(request, "This booking has already been cancelled.")
            return redirect('customer-bookings')

        max_retries = 3
        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    booking_obj = Booking.objects.select_for_update().get(pk=booking.pk)
                    if booking_obj.status == Booking.Status.CANCELLED:
                        messages.info(request, "This booking has already been cancelled.")
                        return redirect('customer-bookings')

                    event = Event.objects.select_for_update().get(pk=booking_obj.event.pk)
                    event.available_seats += booking_obj.quantity
                    event.save(update_fields=['available_seats'])

                    booking_obj.status = Booking.Status.CANCELLED
                    booking_obj.save(update_fields=['status'])

                    messages.success(request, f"Booking #{booking_obj.id} for '{event.name}' cancelled successfully.")
                    return redirect('customer-bookings')
            except DatabaseError:
                if attempt == max_retries - 1:
                    messages.error(request, "Server busy. Please try cancelling again.")
                    return redirect('customer-bookings')
                time.sleep(0.05 * (2 ** attempt))

        return redirect('customer-bookings')


class CustomerReferralView(CustomerRequiredMixin, TemplateView):
    template_name = 'customer/referrals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        node = get_or_create_referral_node(self.request.user)
        context['referral_node'] = node
        context['tree_dict'] = build_tree_dict(node)
        context['team_stats'] = get_team_stats(node)
        return context


class LandingPageView(TemplateView):
    template_name = 'landing.html'
