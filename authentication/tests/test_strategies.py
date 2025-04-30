from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from authentication.strategies import LoginResponseStrategy, InvalidCredentialsStrategy, LockedAccountStrategy, SuccessfulLoginStrategy

class LoginResponseStrategyTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = APIView()
        self.tokens = {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token"
        }

    def test_base_login_response_strategy(self):
        """Test the base LoginResponseStrategy abstract class"""
        
        strategy = LoginResponseStrategy()
        
        self.assertIsInstance(strategy, LoginResponseStrategy)
        
        result = strategy.handle_response(self.tokens)
        self.assertIsNone(result)
        
        self.assertIsNone(strategy.handle_response({}))
        self.assertIsNone(strategy.handle_response(None))
        self.assertIsNone(strategy.handle_response({"message": "test"}))

    def test_successful_login_strategy(self):
        """Test successful login response strategy"""
        strategy = SuccessfulLoginStrategy()
        response = strategy.handle_response(self.tokens)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "Login successful")
        self.assertEqual(response.data["access_token"], self.tokens["access_token"])

    def test_locked_account_strategy(self):
        """Test locked account response strategy"""
        strategy = LockedAccountStrategy()
        response = strategy.handle_response({"message": "Account is locked"})
        
        self.assertEqual(response.status_code, 423)
        self.assertEqual(response.data["detail"], "Account is locked")

    def test_invalid_credentials_strategy(self):
        """Test invalid credentials response strategy"""
        strategy = InvalidCredentialsStrategy()
        response = strategy.handle_response({})
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Invalid email or password")