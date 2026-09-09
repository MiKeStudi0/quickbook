import concurrent.futures
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITransactionTestCase, APIClient
from django.contrib.auth import get_user_model
from django.db import connection

from events.models import Event
from bookings.models import Booking

User = get_user_model()

class BookingAPITests(APITransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="customer_user",
            email="customer@example.com",
            password="password123"
        )
        self.client.force_authenticate(user=self.user)

        self.event = Event.objects.create(
            name="Exclusive Workshop",
            description="Limited capacity event",
            venue="Room 101",
            event_date=timezone.now() + timedelta(days=5),
            total_seats=5,
            available_seats=5
        )

        self.book_url = reverse('event-book', args=[self.event.id])
        self.history_url = reverse('booking-history')

    def test_book_event_success(self):
        response = self.client.post(self.book_url, {"quantity": 2}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["quantity"], 2)
        self.assertEqual(response.data["status"], "CONFIRMED")

        self.event.refresh_from_db()
        self.assertEqual(self.event.available_seats, 3)

    def test_book_event_insufficient_seats(self):
        response = self.client.post(self.book_url, {"quantity": 10}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Not enough seats", response.data["detail"])

        self.event.refresh_from_db()
        self.assertEqual(self.event.available_seats, 5)

    def test_book_event_invalid_quantity(self):
        response = self.client.post(self.book_url, {"quantity": 0}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_neg = self.client.post(self.book_url, {"quantity": -2}, format='json')
        self.assertEqual(response_neg.status_code, status.HTTP_400_BAD_REQUEST)

        self.event.refresh_from_db()
        self.assertEqual(self.event.available_seats, 5)

    def test_cancel_booking(self):
        book_resp = self.client.post(self.book_url, {"quantity": 3}, format='json')
        booking_id = book_resp.data["id"]

        cancel_url = reverse('booking-cancel', args=[booking_id])
        cancel_resp = self.client.post(cancel_url)
        self.assertEqual(cancel_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(cancel_resp.data["status"], "CANCELLED")

        self.event.refresh_from_db()
        self.assertEqual(self.event.available_seats, 5)

        # Attempt to cancel again
        re_cancel_resp = self.client.post(cancel_url)
        self.assertEqual(re_cancel_resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_booking_history(self):
        self.client.post(self.book_url, {"quantity": 1}, format='json')
        self.client.post(self.book_url, {"quantity": 2}, format='json')

        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_concurrent_two_users_booking_four_seats_each(self):
        # Demonstrates that when available_seats = 5 and two users concurrently request 4 seats each:
        # 1 user succeeds (4 seats booked, available_seats = 1), and 1 user fails.
        # It NEVER results in negative available_seats (-3) or 8 seats booked!
        user1 = User.objects.create_user(username="con_user1", email="cu1@example.com", password="pwd")
        user2 = User.objects.create_user(username="con_user2", email="cu2@example.com", password="pwd")

        event_id = self.event.id
        connection.close()

        def try_book(user):
            client = APIClient()
            client.force_authenticate(user=user)
            return client.post(f"/api/events/{event_id}/book/", {"quantity": 4}, format='json')

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(try_book, user1)
            f2 = executor.submit(try_book, user2)
            res1 = f1.result()
            res2 = f2.result()

        successes = [r for r in [res1, res2] if r.status_code == status.HTTP_201_CREATED]
        failures = [r for r in [res1, res2] if r.status_code == status.HTTP_400_BAD_REQUEST]

        self.assertEqual(len(successes), 1)
        self.assertEqual(len(failures), 1)

        self.event.refresh_from_db()
        self.assertEqual(self.event.available_seats, 1)
        self.assertNotEqual(self.event.available_seats, -3)

    def test_concurrent_booking_prevention_of_overselling(self):
        # Verify that total booked seats never exceed available seats under concurrent requests.
        users = []
        for i in range(10):
            u = User.objects.create_user(username=f"user_{i}", email=f"user_{i}@example.com", password="pwd")
            users.append(u)

        event_id = self.event.id
        connection.close()

        def make_booking(user):
            client = APIClient()
            client.force_authenticate(user=user)
            return client.post(f"/api/events/{event_id}/book/", {"quantity": 1}, format='json')

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_booking, u) for u in users]
            results = [f.result() for f in futures]

        successful_bookings = [r for r in results if r.status_code == status.HTTP_201_CREATED]

        self.assertEqual(len(successful_bookings), 5)

        self.event.refresh_from_db()
        self.assertEqual(self.event.available_seats, 0)
