from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from pt_backend.services import CasesSummaryFilterService
from pt_backend.views import CasesSummaryFilterStatsView

class CasesSummaryFilterStatsViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('dashboard-stats')
        
        # Sample response data from the service
        self.mock_results = {
            "disease_stats": [{"name": "COVID-19", "severity_counts": {"hospitalisasi": 10, "insiden": 5, "mortalitas": 2}, "total_cases": 17}],
            "province_stats": [{"name": "DKI Jakarta", "severity_counts": {"hospitalisasi": 8, "insiden": 3, "mortalitas": 1}, "total_cases": 12}],
            "city_stats": [{"name": "Jakarta", "severity_counts": {"hospitalisasi": 6, "insiden": 2, "mortalitas": 1}, "total_cases": 9}]
        }
    
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_get_no_filters(self, MockService):
        """Test the GET method with no filters applied"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Make request
        response = self.client.get(self.url)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=None,
            provinces=None,
            cities=None,
            news_portals=None,
            alert_levels=None,
            date_range=None
        )
        self.assertEqual(response.json(), self.mock_results)
    
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_get_with_disease_filter(self, MockService):
        """Test the GET method with disease filter"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Make request with disease filter
        response = self.client.get(f"{self.url}?disease=COVID-19")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=['COVID-19'],
            provinces=None,
            cities=None,
            news_portals=None,
            alert_levels=None,
            date_range=None
        )
    
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_get_with_province_filter(self, MockService):
        """Test the GET method with province filter"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Make request with province filter
        response = self.client.get(f"{self.url}?province=DKI+Jakarta")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=None,
            provinces=['DKI Jakarta'],
            cities=None,
            news_portals=None,
            alert_levels=None,
            date_range=None
        )
    
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_get_with_city_filter(self, MockService):
        """Test the GET method with city filter"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Make request with city filter
        response = self.client.get(f"{self.url}?city=Jakarta")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=None,
            provinces=None,
            cities=['Jakarta'],
            news_portals=None,
            alert_levels=None,
            date_range=None
        )
    
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_get_with_news_portal_filter(self, MockService):
        """Test the GET method with news portal filter"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Make request with news portal filter
        response = self.client.get(f"{self.url}?news_portal=Kompas")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=None,
            provinces=None,
            cities=None,
            news_portals=['Kompas'],
            alert_levels=None,
            date_range=None
        )
    
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_get_with_alert_level_filter(self, MockService):
        """Test the GET method with alert level filter"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Make request with alert level filter
        response = self.client.get(f"{self.url}?alert_level=Bahaya")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=None,
            provinces=None,
            cities=None,
            news_portals=None,
            alert_levels=['Bahaya'],
            date_range=None
        )
    
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_get_with_date_range_filter(self, MockService):
        """Test the GET method with date range filter"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Make request with date range filter
        response = self.client.get(f"{self.url}?start_date=2023-01-01&end_date=2023-12-31")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=None,
            provinces=None,
            cities=None,
            news_portals=None,
            alert_levels=None,
            date_range=('2023-01-01', '2023-12-31')
        )
    
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_get_with_multiple_filters(self, MockService):
        """Test the GET method with multiple filters"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Make request with multiple filters
        response = self.client.get(
            f"{self.url}?disease=COVID-19&province=DKI+Jakarta&city=Jakarta" +
            "&news_portal=Kompas&alert_level=Bahaya&start_date=2023-01-01&end_date=2023-12-31"
        )
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=['COVID-19'],
            provinces=['DKI Jakarta'],
            cities=['Jakarta'],
            news_portals=['Kompas'],
            alert_levels=['Bahaya'],
            date_range=('2023-01-01', '2023-12-31')
        )
    
    @patch('pt_backend.views.CasesSummaryFilterService')
    def test_get_with_multiple_values_for_same_parameter(self, MockService):
        """Test the GET method with multiple values for the same parameter"""
        # Setup mock
        mock_service_instance = MagicMock(spec=CasesSummaryFilterService)
        mock_service_instance.get_filter_stats.return_value = self.mock_results
        MockService.return_value = mock_service_instance
        
        # Make request with multiple values for same parameter
        response = self.client.get(
            f"{self.url}?disease=COVID-19&disease=Dengue&province=DKI+Jakarta&province=Jawa+Barat"
        )
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_service_instance.get_filter_stats.assert_called_once_with(
            diseases=['COVID-19', 'Dengue'],
            provinces=['DKI Jakarta', 'Jawa Barat'],
            cities=None,
            news_portals=None,
            alert_levels=None,
            date_range=None
        )