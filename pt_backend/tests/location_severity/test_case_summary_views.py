from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from pt_backend.authentication import APIKeyAuthentication
from pt_backend.services import CasesSummaryFilterService
from pt_backend.models import Location
from rest_framework import status


class CasesSummaryFilterStatsPostViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('dashboard-stats')
        
        # Sample response data from the service
        self.mock_results = {
            "disease_stats": [{"name": "COVID-19", "severity_counts": {"hospitalisasi": 10, "insiden": 5, "mortalitas": 2}, "total_cases": 17}],
            "province_stats": [{"name": "DKI Jakarta", "severity_counts": {"hospitalisasi": 8, "insiden": 3, "mortalitas": 1}, "total_cases": 12}],
            "city_stats": [{"name": "Jakarta", "severity_counts": {"hospitalisasi": 6, "insiden": 2, "mortalitas": 1}, "total_cases": 9}]
        }
    
    @patch.object(APIKeyAuthentication, 'authenticate', return_value=None)
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_post_with_diseases(self, MockService, mock_auth):
        """Test POST with disease filter"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Make request with disease filter
        response = self.client.post(
            self.url,
            data={"diseases": ["COVID-19", "Dengue"]},
            format='json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=["COVID-19", "Dengue"],
            provinces=None,
            cities=None,
            news_portals=None,
            alert_levels=None,
            date_range=None
        )
        self.assertEqual(response.json(), self.mock_results)
    
    @patch.object(APIKeyAuthentication, 'authenticate', return_value=None)
    @patch('pt_backend.views.Location.objects.filter')
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_post_with_cities_to_provinces(self, MockService, MockLocationFilter, mock_auth):
        """Test POST with locations that get converted to provinces"""
        # Setup mocks
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Mock the Location queryset
        mock_values_list = MagicMock()
        mock_values_list.distinct.return_value = ["DKI Jakarta", "Jawa Barat"]
        MockLocationFilter.return_value.values_list.return_value = mock_values_list
        
        # Make request with locations
        response = self.client.post(
            self.url,
            data={"locations": ["Jakarta", "Bandung"]},
            format='json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        MockLocationFilter.assert_called_once_with(city__in=["Jakarta", "Bandung"])
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=None,
            provinces=["DKI Jakarta", "Jawa Barat"],
            cities=["Jakarta", "Bandung"],
            news_portals=None,
            alert_levels=None,
            date_range=None
        )
    
    @patch.object(APIKeyAuthentication, 'authenticate', return_value=None)
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_post_with_portals(self, MockService, mock_auth):
        """Test POST with news portals filter"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Make request with news portals
        response = self.client.post(
            self.url,
            data={"portals": ["Kompas", "Detik"]},
            format='json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=None,
            provinces=None,
            cities=None,
            news_portals=["Kompas", "Detik"],
            alert_levels=None,
            date_range=None
        )
    
    @patch.object(APIKeyAuthentication, 'authenticate', return_value=None)
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_post_with_level_of_alertness_as_string(self, MockService, mock_auth):
        """Test POST with level_of_alertness as string that gets converted to int"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Make request with level_of_alertness as string
        response = self.client.post(
            self.url,
            data={"level_of_alertness": "2"},
            format='json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=None,
            provinces=None,
            cities=None,
            news_portals=None,
            alert_levels=2,  # Should be converted to integer
            date_range=None
        )
    
    @patch.object(APIKeyAuthentication, 'authenticate', return_value=None)
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_post_with_date_range(self, MockService, mock_auth):
        """Test POST with date range"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Make request with date range
        response = self.client.post(
            self.url,
            data={
                "start_date": "2023-01-01",
                "end_date": "2023-12-31"
            },
            format='json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=None,
            provinces=None,
            cities=None,
            news_portals=None,
            alert_levels=None,
            date_range=("2023-01-01", "2023-12-31")
        )
    
    @patch.object(APIKeyAuthentication, 'authenticate', return_value=None)
    @patch('pt_backend.views.Location.objects.filter')
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_post_with_all_filters(self, MockService, MockLocationFilter, mock_auth):
        """Test POST with all filter types combined"""
        # Setup mocks
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Mock the Location queryset
        mock_values_list = MagicMock()
        mock_values_list.distinct.return_value = ["DKI Jakarta"]
        MockLocationFilter.return_value.values_list.return_value = mock_values_list
        
        # Make request with all filters
        response = self.client.post(
            self.url,
            data={
                "diseases": ["COVID-19"],
                "locations": ["Jakarta"],
                "portals": ["Kompas"],
                "level_of_alertness": "3",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31"
            },
            format='json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=["COVID-19"],
            provinces=["DKI Jakarta"],
            cities=["Jakarta"],
            news_portals=["Kompas"],
            alert_levels=3,
            date_range=("2023-01-01", "2023-12-31")
        )
    
    @patch.object(APIKeyAuthentication, 'authenticate', return_value=None)
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_post_with_invalid_level_of_alertness(self, MockService, mock_auth):
        """Test POST with invalid level_of_alertness"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        MockService.return_value = mock_service_instance
        
        # Make request with invalid level_of_alertness
        response = self.client.post(
            self.url,
            data={"level_of_alertness": "not-a-number"},
            format='json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("invalid literal for int()", response.data["error"])
        mock_service_instance.get_filter_stats.assert_not_called()
    
    @patch.object(APIKeyAuthentication, 'authenticate', return_value=None)
    @patch('pt_backend.views.Location.objects.filter')
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_post_with_empty_locations(self, MockService, MockLocationFilter, mock_auth):
        """Test POST with empty locations list"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Make request with empty locations
        response = self.client.post(
            self.url,
            data={"locations": []},
            format='json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        MockLocationFilter.assert_not_called()  # Should not query for provinces
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=None,
            provinces=None,
            cities=None,
            news_portals=None,
            alert_levels=None,
            date_range=None
        )
    
    @patch.object(APIKeyAuthentication, 'authenticate', return_value=None)
    @patch('pt_backend.views.CasesSummaryFilterService.get_filter_stats')
    def test_post_with_service_exception(self, mock_get_filter_stats, mock_auth):
        """Test error handling when service raises an exception"""
        # Setup mock to raise exception
        mock_get_filter_stats.side_effect = Exception("Test service error")
        
        # Make request
        response = self.client.post(
            self.url,
            data={"diseases": ["COVID-19"]},
            format='json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("Test service error", response.data["error"])