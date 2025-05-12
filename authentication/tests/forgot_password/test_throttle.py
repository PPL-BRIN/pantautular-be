from django.test import TestCase, RequestFactory
from authentication.throttling import PasswordResetRateThrottle


class TestPasswordResetThrottling(TestCase):
    """Tests for the PasswordResetRateThrottle class"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.throttle = PasswordResetRateThrottle()
        
    def test_throttle_scope(self):
        """Test that the throttle has the correct scope"""
        self.assertEqual(self.throttle.scope, 'password_reset')
    
    def test_get_cache_key(self):
        """Test that get_cache_key returns the request identifier"""
        request = self.factory.post('/api/reset-password/')
        
        # Mock a view for the throttle
        view = type('MockView', (), {})()
        
        # Get the cache key
        cache_key = self.throttle.get_cache_key(request, view)
        
        # It should match what get_ident would return
        expected_key = self.throttle.get_ident(request)
        self.assertEqual(cache_key, expected_key)