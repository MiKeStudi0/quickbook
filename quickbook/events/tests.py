from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Event

User = get_user_model()

class EventAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="vendor_user",
            email="vendor@example.com",
            password="password123",
            is_vendor=True
        )
        self.client.force_authenticate(user=self.user)

        self.list_url = reverse('event-list')

        self.event1 = Event.objects.create(
            name="Tech Conference 2026",
            description="Annual tech meet",
            venue="Silicon Convention Center",
            event_date=timezone.now() + timedelta(days=10),
            total_seats=100,
            available_seats=100,
            vendor=self.user
        )

        self.event2 = Event.objects.create(
            name="Music Festival",
            description="Live concert",
            venue="Grand Arena",
            event_date=timezone.now() + timedelta(days=20),
            total_seats=50,
            available_seats=0,
            vendor=self.user
        )

    def test_list_events_pagination(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], 2)

    def test_get_event_detail(self):
        self.client.logout()
        detail_url = reverse('event-detail', args=[self.event1.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Tech Conference 2026")

    def test_create_event(self):
        event_data = {
            "name": "Design Summit",
            "description": "UI/UX talks",
            "venue": "Art Hall",
            "event_date": (timezone.now() + timedelta(days=5)).isoformat(),
            "total_seats": 200
        }
        response = self.client.post(self.list_url, event_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["available_seats"], 200)
        self.assertEqual(response.data["vendor_username"], "vendor_user")

    def test_patch_event(self):
        detail_url = reverse('event-detail', args=[self.event1.id])
        patch_data = {"name": "Tech Conference 2026 (Updated)"}
        response = self.client.patch(detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Tech Conference 2026 (Updated)")

    def test_search_events(self):
        response = self.client.get(f"{self.list_url}?search=Music")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Music Festival")

    def test_filter_available_events(self):
        response = self.client.get(f"{self.list_url}?is_available=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Tech Conference 2026")
