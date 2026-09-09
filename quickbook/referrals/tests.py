from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from referrals.models import ReferralNode

User = get_user_model()

class ReferralNetworkAPITests(APITestCase):

    def setUp(self):
        self.register_url = reverse('auth-register')

        # Register User A (Root)
        r_a = self.client.post(self.register_url, {
            "username": "user_a",
            "email": "a@example.com",
            "password": "password123"
        }, format='json')
        self.user_a = User.objects.get(id=r_a.data["user"]["id"])
        self.code_a = r_a.data["user"]["referral_code"]

        # Register User B using A's code (Left placement)
        r_b = self.client.post(self.register_url, {
            "username": "user_b",
            "email": "b@example.com",
            "password": "password123",
            "referral_code": self.code_a
        }, format='json')
        self.user_b = User.objects.get(id=r_b.data["user"]["id"])

        # Register User C using A's code (Right placement)
        r_c = self.client.post(self.register_url, {
            "username": "user_c",
            "email": "c@example.com",
            "password": "password123",
            "referral_code": self.code_a
        }, format='json')
        self.user_c = User.objects.get(id=r_c.data["user"]["id"])

        # Register User D using A's code (should go to B's left)
        r_d = self.client.post(self.register_url, {
            "username": "user_d",
            "email": "d@example.com",
            "password": "password123",
            "referral_code": self.code_a
        }, format='json')
        self.user_d = User.objects.get(id=r_d.data["user"]["id"])

        # Register User E using A's code (should go to B's right)
        r_e = self.client.post(self.register_url, {
            "username": "user_e",
            "email": "e@example.com",
            "password": "password123",
            "referral_code": self.code_a
        }, format='json')
        self.user_e = User.objects.get(id=r_e.data["user"]["id"])

    def test_left_and_right_placement_structure(self):
        node_a = ReferralNode.objects.get(user=self.user_a)
        node_b = ReferralNode.objects.get(user=self.user_b)
        node_c = ReferralNode.objects.get(user=self.user_c)
        node_d = ReferralNode.objects.get(user=self.user_d)
        node_e = ReferralNode.objects.get(user=self.user_e)

        # A's immediate children: B on left, C on right
        self.assertEqual(node_a.left, node_b)
        self.assertEqual(node_a.right, node_c)

        # B's immediate children: D on left, E on right
        self.assertEqual(node_b.left, node_d)
        self.assertEqual(node_b.right, node_e)

    def test_referral_tree_api(self):
        tree_url = reverse('referral-tree', args=[self.user_a.id])
        response = self.client.get(tree_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "user_a")
        self.assertEqual(response.data["left"]["username"], "user_b")
        self.assertEqual(response.data["right"]["username"], "user_c")
        self.assertEqual(response.data["left"]["left"]["username"], "user_d")

    def test_referral_root_api(self):
        root_url = reverse('referral-root', args=[self.user_e.id])
        response = self.client.get(root_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "user_a")

    def test_referral_stats_api(self):
        stats_url = reverse('referral-stats', args=[self.user_a.id])
        response = self.client.get(stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Left side of A has B, D, E (3 nodes)
        self.assertEqual(response.data["left_team_count"], 3)
        # Right side of A has C (1 node)
        self.assertEqual(response.data["right_team_count"], 1)
        self.assertEqual(response.data["total_team_count"], 4)

    def test_invalid_referral_code_rejection(self):
        response = self.client.post(self.register_url, {
            "username": "invalid_ref_user",
            "email": "invalid@example.com",
            "password": "password123",
            "referral_code": "INVALID_CODE_999"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("referral_code", response.data)
