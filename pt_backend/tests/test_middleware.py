from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from unittest.mock import patch, MagicMock
from pt_backend.middleware import SentryContextMiddleware
from pt_backend.models import User

class SentryContextMiddlewareTests(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SentryContextMiddleware(get_response=lambda r: None)
        
        # Buat user untuk testing
        self.user = User(
            id=1,
            name="Test User",
            email="test@example.com",
            role="TENAGA_AHLI",
        )
    
    @patch('pt_backend.middleware.configure_scope')
    def test_process_request_with_authenticated_user(self, mock_configure_scope):
        """Test middleware with authenticated user correctly sets user context"""
        # Setup
        request = self.factory.get('/test-path')
        request.user = self.user
        
        # Mock the context manager
        mock_scope = MagicMock()
        mock_configure_scope.return_value.__enter__.return_value = mock_scope
        
        # Execute
        self.middleware.process_request(request)
        
        # Verify
        mock_scope.set_tag.assert_any_call("http_method", "GET")
        mock_scope.set_tag.assert_any_call("endpoint", "/test-path")
        
        # Verify user context was set correctly
        mock_scope.set_user.assert_called_once_with({
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
        })
    
    @patch('pt_backend.middleware.configure_scope')
    def test_process_request_with_anonymous_user(self, mock_configure_scope):
        """Test middleware with anonymous user sets default context"""
        # Setup
        request = self.factory.get('/test-path')
        request.user = AnonymousUser()
        
        # Mock the context manager
        mock_scope = MagicMock()
        mock_configure_scope.return_value.__enter__.return_value = mock_scope
        
        # Patch the _get_client_ip method to return a known value
        with patch.object(self.middleware, '_get_client_ip', return_value='127.0.0.1'):
            # Execute
            self.middleware.process_request(request)
        
        # Verify
        mock_scope.set_user.assert_called_once_with({
            "id": None,
            "ip_address": "127.0.0.1",
            "authenticated": False
        })
    
    @patch('pt_backend.middleware.configure_scope')
    def test_process_request_with_user_missing_attributes(self, mock_configure_scope):
        """Test middleware handles users with missing name or email attributes"""
        # Setup a user without name attribute
        user_without_name = type('UserWithoutName', (), {'id': 2, 'email': 'noname@example.com'})()
        request = self.factory.get('/test-path')
        request.user = user_without_name
        
        # Mock the context manager
        mock_scope = MagicMock()
        mock_configure_scope.return_value.__enter__.return_value = mock_scope
        
        # Execute
        self.middleware.process_request(request)
        
        # Verify - name should be None
        mock_scope.set_user.assert_called_once_with({
            "id": 2,
            "name": None,
            "email": "noname@example.com",
        })
    
    def test_get_client_ip_with_x_forwarded_for(self):
        """Test _get_client_ip method correctly parses X-Forwarded-For header"""
        # Setup
        request = self.factory.get('/test-path')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1, 172.16.0.1'
        
        # Execute
        ip = self.middleware._get_client_ip(request)
        
        # Verify - should get the first IP in the list
        self.assertEqual(ip, '192.168.1.1')
    
    def test_get_client_ip_without_x_forwarded_for(self):
        """Test _get_client_ip method falls back to REMOTE_ADDR when X-Forwarded-For is missing"""
        # Setup
        request = self.factory.get('/test-path')
        request.META['REMOTE_ADDR'] = '192.168.1.2'
        
        # Execute
        ip = self.middleware._get_client_ip(request)
        
        # Verify
        self.assertEqual(ip, '192.168.1.2')
    
    def test_get_client_ip_with_no_ip_information(self):
        """Test _get_client_ip method returns 'unknown' when no IP info is available"""
        # Setup - Request without any IP information
        request = self.factory.get('/test-path')
        # Pastikan tidak ada IP di META
        if 'REMOTE_ADDR' in request.META:
            del request.META['REMOTE_ADDR']
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            del request.META['HTTP_X_FORWARDED_FOR']
        
        # Execute
        ip = self.middleware._get_client_ip(request)
        
        # Verify
        self.assertEqual(ip, 'unknown')

    @patch('pt_backend.middleware.configure_scope')
    def test_integration_with_real_sentry_sdk(self, mock_configure_scope):
        """Integration test to ensure middleware works with actual sentry_sdk scope"""
        # Setup real request with authenticated user
        request = self.factory.get('/api/cases')
        request.user = self.user
        
        # Execute middleware with the mocked scope
        mock_scope = MagicMock()
        mock_configure_scope.return_value.__enter__.return_value = mock_scope
        
        self.middleware.process_request(request)
        
        # Verify tags and user were set
        self.assertTrue(mock_scope.set_tag.call_count >= 2)
        mock_scope.set_user.assert_called_once()