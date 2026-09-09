from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthAPITests(APITestCase):

    def setUp(self):
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.logout_url = reverse('auth-logout')
        self.me_url = reverse('auth-me')

        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123",
            "is_vendor": False
        }

    def test_register_user(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertEqual(response.data["user"]["username"], "testuser")
        self.assertIsNotNone(response.data["user"]["referral_code"])

    def test_register_with_referral_code(self):
        # Register first user
        reg1 = self.client.post(self.register_url, self.user_data, format='json')
        ref_code = reg1.data["user"]["referral_code"]

        # Register second user with referral code
        user2_data = {
            "username": "referreduser",
            "email": "referred@example.com",
            "password": "password123",
            "referral_code": ref_code
        }
        reg2 = self.client.post(self.register_url, user2_data, format='json')
        self.assertEqual(reg2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(reg2.data["user"]["referred_by_code"], ref_code)

    def test_login_user(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)

    def test_login_invalid_credentials(self):
        self.client.post(self.register_url, self.user_data, format='json')
        invalid_login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, invalid_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_protected_me_endpoint(self):
        reg_resp = self.client.post(self.register_url, self.user_data, format='json')
        access_token = reg_resp.data["tokens"]["access"]

        # Request without header
        unauth_resp = self.client.get(self.me_url)
        self.assertEqual(unauth_resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # Request with Bearer token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        auth_resp = self.client.get(self.me_url)
        self.assertEqual(auth_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(auth_resp.data["username"], "testuser")

    def test_logout_user(self):
        reg_resp = self.client.post(self.register_url, self.user_data, format='json')
        access_token = reg_resp.data["tokens"]["access"]
        refresh_token = reg_resp.data["tokens"]["refresh"]

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_resp = self.client.post(self.logout_url, {"refresh": refresh_token}, format='json')
        self.assertEqual(logout_resp.status_code, status.HTTP_200_OK)
