from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.db.models import Q

from events.models import Event
from bookings.models import Booking
from referrals.services import get_or_create_referral_node, build_tree_dict, get_team_stats
from .forms import StaffLoginForm, VendorForm, EventForm

User = get_user_model()

class StaffRequiredMixin(UserPassesTestMixin):
    login_url = '/dashboard/login/'

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_vendor:
                return redirect('dashboard-event-list')
            return redirect('customer-events')
        return redirect('dashboard-login')


class DashboardAccessMixin(UserPassesTestMixin):
    login_url = '/dashboard/login/'

    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_vendor)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('customer-events')
        return redirect('dashboard-login')


class StaffLoginView(LoginView):
    template_name = 'dashboard/login.html'
    authentication_form = StaffLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if not (user.is_staff or user.is_vendor):
            from django.contrib.auth import login
            login(self.request, user)
            return redirect('customer-events')
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated and user.is_vendor and not user.is_staff:
            return reverse_lazy('dashboard-event-list')
        return reverse_lazy('dashboard-home')


class StaffLogoutView(LogoutView):
    next_page = reverse_lazy('dashboard-login')


class DashboardHomeView(StaffRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_customers'] = User.objects.filter(is_staff=False, is_vendor=False).count()
        context['total_vendors'] = User.objects.filter(is_vendor=True).count()
        context['total_events'] = Event.objects.count()
        context['total_bookings'] = Booking.objects.count()
        context['recent_bookings'] = Booking.objects.select_related('user', 'event').order_by('-created_at')[:5]
        context['upcoming_events'] = Event.objects.order_by('event_date')[:5]
        return context


class VendorListView(StaffRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/vendor_list.html'
    context_object_name = 'vendors'
    paginate_by = 10

    def get_queryset(self):
        qs = User.objects.filter(is_vendor=True).order_by('-created_at')
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(Q(username__icontains=query) | Q(email__icontains=query))
        return qs


class VendorCreateView(StaffRequiredMixin, CreateView):
    model = User
    form_class = VendorForm
    template_name = 'dashboard/vendor_form.html'
    success_url = reverse_lazy('dashboard-vendor-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Add Vendor"
        return context


class VendorUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = VendorForm
    template_name = 'dashboard/vendor_form.html'
    success_url = reverse_lazy('dashboard-vendor-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edit Vendor"
        return context


class EventListView(DashboardAccessMixin, ListView):
    model = Event
    template_name = 'dashboard/event_list.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_template_names(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or self.request.GET.get('ajax') == '1':
            return ['dashboard/partials/event_table.html']
        return [self.template_name]

    def get_queryset(self):
        qs = Event.objects.select_related('vendor').order_by('-created_at')
        if self.request.user.is_vendor and not self.request.user.is_staff:
            qs = qs.filter(vendor=self.request.user)
        
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




class EventCreateView(DashboardAccessMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'dashboard/event_form.html'
    success_url = reverse_lazy('dashboard-event-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.is_vendor and not self.request.user.is_staff:
            form.fields['vendor'].queryset = User.objects.filter(id=self.request.user.id)
            form.fields['vendor'].initial = self.request.user.id
        return form

    def form_valid(self, form):
        if self.request.user.is_vendor and not self.request.user.is_staff:
            form.instance.vendor = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Add Event"
        return context


class EventUpdateView(DashboardAccessMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'dashboard/event_form.html'
    success_url = reverse_lazy('dashboard-event-list')

    def get_queryset(self):
        qs = Event.objects.all()
        if self.request.user.is_vendor and not self.request.user.is_staff:
            qs = qs.filter(vendor=self.request.user)
        return qs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.is_vendor and not self.request.user.is_staff:
            form.fields['vendor'].queryset = User.objects.filter(id=self.request.user.id)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edit Event"
        return context


class UserListView(StaffRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/user_list.html'
    context_object_name = 'users_list'
    paginate_by = 10

    def get_queryset(self):
        qs = User.objects.all().order_by('-created_at')
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(referral_code__icontains=query)
            )
        return qs


class UserDetailView(StaffRequiredMixin, DetailView):
    model = User
    template_name = 'dashboard/user_detail.html'
    context_object_name = 'target_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        node = get_or_create_referral_node(user)
        context['user_bookings'] = Booking.objects.filter(user=user).select_related('event').order_by('-created_at')
        context['referral_node'] = node
        context['tree_dict'] = build_tree_dict(node)
        context['team_stats'] = get_team_stats(node)
        return context

