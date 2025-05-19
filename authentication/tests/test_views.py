from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APIClient
import os
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory
from authentication.views import SignupAPIView
from pt_backend.models import User
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

client = APIClient()


@override_settings(SECRET_API_KEYS=["testkey"])          
class SignupAPIViewTests(TestCase):
    """Black-box tests for the sign-up endpoint secured by API-key auth."""

    def _post(self, payload, api_key="testkey"):
        """
        POST to the real URL resolved by its name (`sign-up`) so changes
        in urls.py never break the tests.
        """
        url = reverse("sign-up")              
        return client.post(
            url,
            payload,
            format="json",
            HTTP_X_API_KEY=api_key,
        )

    def test_signup_happy_path(self):
        res = self._post(
            {"name": "Ken", "email": "ken@example.com", "password": "5up3rSafe!"} # NOSONAR – test data, not a real secret
        )

        self.assertEqual(res.status_code, 201)
        self.assertTrue(
            User.objects.filter(id=res.data["id"], email="ken@example.com").exists()
        )

    def test_duplicate_email_returns_400(self):
        self._post(
            {"name": "Ken", "email": "dup@ex.com", "password": "Sup3rSafe!"} # NOSONAR – test data, not a real secret
        )

        res = self._post(
            {"name": "Clone", "email": "dup@ex.com", "password": "OtherSafe12!"} # NOSONAR – test data, not a real secret
        )

        self.assertEqual(res.status_code, 400)
        self.assertIn("already exists", res.data["detail"])

    def test_service_rejects_password_returns_400(self):
        """
        Password passes serializer (>8 chars) but RegistrationService vetoes it.
        """
        with patch(
            "authentication.registration.service.validate_password",
            side_effect=ValidationError("Too weak"),
        ):
            res = self._post(
                {"name": "Weak", "email": "weak@ex.com", "password": "WeakPass1"} # NOSONAR – test data, not a real secret
            )

        self.assertEqual(res.status_code, 400)
        self.assertIn("Too weak", res.data["detail"])

    def test_missing_password_returns_400(self):
        res = self._post({"name": "NoPwd", "email": "np@ex.com"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("password", res.data)

    def test_missing_or_wrong_api_key_returns_401(self):
        res = self._post(
            {"name": "Ken", "email": "wrongkey@ex.com", "password": "5up3rSafe!"}, # NOSONAR – test data, not a real secret
            api_key="badkey",
        )
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid API key", res.data["detail"])

class LoginAPIViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('login')
        
        # Mock API key validation
        patcher = patch('authentication.security.APIKeyAuthentication.authenticate')
        self.mock_auth = patcher.start()
        self.mock_auth.return_value = (None, None)  # Authentication always passes
        self.addCleanup(patcher.stop)

    @patch('authentication.views.AuthService')
    def test_successful_login(self, mock_auth_service):
        """Test successful login request - happy path"""
        # Configure mock
        mock_auth_service_instance = mock_auth_service.return_value
        mock_auth_service_instance.login.return_value = {'access_token': 'dummy-token'}
        
        # Make request
        data = {
            'email': 'test@example.com',
            'password': 'Password123!' # NOSONAR – test data, not a real secret
        }
        response = self.client.post(self.url, data, format='json')
        
        # Verify
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Login successful')
        mock_auth_service_instance.login.assert_called_once_with(
            email='test@example.com', 
            password='Password123!' # NOSONAR – test data, not a real secret
        )

    @patch('authentication.views.AuthService')
    def test_invalid_credentials(self, mock_auth_service):
        """Test login with invalid credentials - unhappy path"""
        # Configure mock
        mock_auth_service_instance = mock_auth_service.return_value
        mock_auth_service_instance.login.return_value = None
        
        # Make request
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword123!' # NOSONAR – test data, not a real secret
        }
        response = self.client.post(self.url, data, format='json')
        
        # Verify
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Invalid email or password')

    @patch('authentication.views.AuthService')
    def test_server_error_handling(self, mock_auth_service):
        """Test handling of server errors - edge case"""
        # Configure mock to raise exception
        mock_auth_service_instance = mock_auth_service.return_value
        mock_auth_service_instance.login.side_effect = Exception('Database error')
        
        # Make request
        data = {
            'email': 'test@example.com',
            'password': 'Password123!' # NOSONAR – test data, not a real secret
        }
        response = self.client.post(self.url, data, format='json')
        
        # Verify
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Login failed. Please try again.')

    def test_invalid_request_data(self):
        """Test login with invalid request format - edge case"""
        # Make request with invalid data
        data = {
            'email': 'not-an-email',
            'password': 'short' # NOSONAR – test data, not a real secret
        }
        response = self.client.post(self.url, data, format='json')
        
        # Verify
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('authentication.views.AuthService')
    def test_account_lockout(self, mock_auth_service):
        """Test login with locked account - account lockout feature"""
        lockout_message = "Account is locked due to too many failed attempts. Try again in 14 minutes and 55 seconds."
        mock_auth_service_instance = mock_auth_service.return_value
        mock_auth_service_instance.login.return_value = {
            'locked': True,
            'message': lockout_message
        }
        
        # Make request
        data = {
            'email': 'test@example.com',
            'password': 'Password123!' # NOSONAR – test data, not a real secret
        }
        response = self.client.post(self.url, data, format='json')
        
        # Verify
        self.assertEqual(response.status_code, status.HTTP_423_LOCKED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], lockout_message)
        mock_auth_service_instance.login.assert_called_once_with(
            email='test@example.com', 
            password='Password123!' # NOSONAR – test data, not a real secret
        )





VERIFY_URL = reverse("verify-email")  # "/authentication/verify-email/"


class VerifyEmailAPIViewTests(TestCase):
    """Covers every code path of VerifyEmailAPIView."""

    # ------------------------------------------------------------------ #
    #                           HAPPY PATH                               #
    # ------------------------------------------------------------------ #
    def test_verify_email_success(self):
        user = User.objects.create(
            name="Ken", email="ken@example.com", password="x", is_active=False #NOSONAR
        )

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token  = default_token_generator.make_token(user)

        resp = self.client.get(VERIFY_URL, {"uid": uidb64, "token": token})

        self.assertEqual(resp.status_code, 200)
        self.assertIn("account activated", resp.json()["detail"].lower())

        # DB side-effect: user now active
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    # ------------------------------------------------------------------ #
    #                 missing uid / token  → 400 BAD REQUEST             #
    # ------------------------------------------------------------------ #
    def test_missing_params_returns_400(self):
        # no params at all
        resp1 = self.client.get(VERIFY_URL)
        self.assertEqual(resp1.status_code, 400)
        self.assertIn("bad request", resp1.json()["detail"].lower())

        # uid present, token missing
        resp2 = self.client.get(VERIFY_URL, {"uid": "abc"})
        self.assertEqual(resp2.status_code, 400)

    # ------------------------------------------------------------------ #
    #        invalid uidb64  OR  non-existent user  → 400 INVALID LINK   #
    # ------------------------------------------------------------------ #
    def test_invalid_uid_or_unknown_user_returns_400(self):
        # completely malformed uid
        resp1 = self.client.get(VERIFY_URL, {"uid": "!", "token": "x"})
        self.assertEqual(resp1.status_code, 400)
        self.assertIn("invalid verification", resp1.json()["detail"].lower())

        # well-formed uid but pk does not exist
        uidb64 = urlsafe_base64_encode(force_bytes(9999))
        resp2  = self.client.get(VERIFY_URL, {"uid": uidb64, "token": "x"})
        self.assertEqual(resp2.status_code, 400)

    # ------------------------------------------------------------------ #
    #          valid uid but **invalid / expired** token  → 400          #
    # ------------------------------------------------------------------ #
    def test_expired_or_invalid_token_returns_400(self):
        user = User.objects.create(
            name="Eva", email="eva@example.com", password="x", is_active=False #NOSONAR
        )
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        # Patch check_token to force False without waiting for expiry
        with patch(
            "authentication.views.default_token_generator.check_token",
            return_value=False,
        ):
            resp = self.client.get(VERIFY_URL, {"uid": uidb64, "token": "bogus"})
            self.assertEqual(resp.status_code, 400)
            self.assertIn("expired or invalid", resp.json()["detail"].lower())

        # User should still be inactive
        user.refresh_from_db()
        self.assertFalse(user.is_active)
