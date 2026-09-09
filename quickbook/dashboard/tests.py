from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from events.models import Event
from bookings.models import Booking

User = get_user_model()

class DashboardViewsTests(TestCase):

    def setUp(self):
        self.staff_user = User.objects.create_superuser(
            username="staff_admin",
            email="staff@example.com",
            password="password123"
        )
        self.customer_user = User.objects.create_user(
            username="normal_customer",
            email="customer@example.com",
            password="password123"
        )

        self.home_url = reverse('dashboard-home')
        self.vendor_list_url = reverse('dashboard-vendor-list')
        self.event_list_url = reverse('dashboard-event-list')
        self.user_list_url = reverse('dashboard-user-list')

    def test_unauthenticated_user_redirected_to_login(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/login/', response.url)

    def test_non_staff_user_access_denied(self):
        self.client.login(username="normal_customer", password="password123")
        response = self.client.get(self.home_url)
        self.assertIn(response.status_code, [403, 302])

    def test_staff_user_dashboard_home_access(self):
        self.client.login(username="staff_admin", password="password123")
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_customers", response.context)
        self.assertIn("total_vendors", response.context)

    def test_staff_vendor_management(self):
        self.client.login(username="staff_admin", password="password123")
        
        # Create vendor
        create_url = reverse('dashboard-vendor-create')
        post_data = {
            "username": "new_vendor_user",
            "email": "vendor_new@example.com",
            "password": "password123",
            "is_vendor": True
        }
        create_resp = self.client.post(create_url, post_data)
        self.assertEqual(create_resp.status_code, 302)

        vendor = User.objects.get(username="new_vendor_user")
        self.assertTrue(vendor.is_vendor)

        # Update vendor
        edit_url = reverse('dashboard-vendor-update', args=[vendor.id])
        edit_resp = self.client.post(edit_url, {
            "username": "new_vendor_user",
            "email": "vendor_updated@example.com",
            "is_vendor": True
        })
        self.assertEqual(edit_resp.status_code, 302)

    def test_staff_user_detail_page(self):
        self.client.login(username="staff_admin", password="password123")
        detail_url = reverse('dashboard-user-detail', args=[self.customer_user.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("referral_node", response.context)
        self.assertIn("team_stats", response.context)
