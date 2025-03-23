from django.test import TestCase
from django.urls import reverse, resolve
from pt_backend.views import LocationSeverityStatsView

class URLsTestCase(TestCase):
    def test_location_severity_stats_url(self):
        """Test the location severity stats URL works correctly"""
        url = reverse('location-severity-stats')
        self.assertEqual(url, '/api/locations/severity-stats/')
        
        resolver = resolve('/api/locations/severity-stats/')
        self.assertEqual(resolver.func.view_class, LocationSeverityStatsView)