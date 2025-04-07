from django.test import TestCase
from unittest.mock import MagicMock, patch
from django.db.models import QuerySet
from pt_backend.services import CaseFilterService, CaseService
from pt_backend.models import Case
from datetime import datetime

class CaseFilterServiceTestCase(TestCase):
    def setUp(self):
        # Create mock case service
        self.mock_case_service = MagicMock(spec=CaseService)
        
        # Create the filter service with mock
        self.filter_service = CaseFilterService(self.mock_case_service)
        
        # Create a mock queryset
        self.mock_queryset = MagicMock(spec=QuerySet)
        # Setup mock QuerySet to return itself after filter() to enable chaining
        self.mock_queryset.filter.return_value = self.mock_queryset
        self.mock_queryset.values.return_value = [{'id': 1}, {'id': 2}]
        
        # Make case service return the mock queryset
        self.mock_case_service.get_all_case.return_value = self.mock_queryset
    
    def test_apply_filters_no_filters(self):
        """Test apply_filters with no filters specified"""
        # Call the method with no filters
        result = self.filter_service.apply_filters()
        
        # Verify case service was called
        self.mock_case_service.get_all_case.assert_called_once()
        
        # Verify no filters were applied (filter method not called)
        self.mock_queryset.filter.assert_not_called()
        
        # Verify original queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_apply_filters_with_diseases(self):
        """Test apply_filters with disease filter"""
        # Call the method with diseases filter
        diseases = ["COVID-19", "Dengue"]
        result = self.filter_service.apply_filters(diseases=diseases)
        
        # Verify filter was called with correct parameters
        self.mock_queryset.filter.assert_called_with(disease__name__in=diseases)
        
        # Verify filtered queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_apply_filters_with_provinces(self):
        """Test apply_filters with province filter"""
        # Call the method with province filter
        provinces = ["DKI Jakarta", "Jawa Barat"]
        result = self.filter_service.apply_filters(provinces=provinces)
        
        # Verify filter was called with correct parameters
        self.mock_queryset.filter.assert_called_with(location__province__in=provinces)
        
        # Verify filtered queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_apply_filters_with_cities(self):
        """Test apply_filters with city filter"""
        # Call the method with city filter
        cities = ["Jakarta", "Bandung"]
        result = self.filter_service.apply_filters(cities=cities)
        
        # Verify filter was called with correct parameters
        self.mock_queryset.filter.assert_called_with(location__city__in=cities)
        
        # Verify filtered queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_apply_filters_with_news_portals(self):
        """Test apply_filters with news portal filter"""
        # Call the method with news portal filter
        news_portals = ["Kompas", "Detik"]
        result = self.filter_service.apply_filters(news_portals=news_portals)
        
        # Verify filter was called with correct parameters
        self.mock_queryset.filter.assert_called_with(news__portal__in=news_portals)
        
        # Verify filtered queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_apply_filters_with_alert_levels(self):
        """Test apply_filters with alert levels filter"""
        # Call the method with alert level filter
        alert_levels = ["Biasa", "Waspada"]
        result = self.filter_service.apply_filters(alert_levels=alert_levels)
        
        # Verify filter was called with correct parameters
        self.mock_queryset.filter.assert_called_with(status__in=alert_levels)
        
        # Verify filtered queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_apply_filters_with_date_range(self):
        """Test apply_filters with date range filter"""
        # Call the method with date range
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        result = self.filter_service.apply_filters(date_range=(start_date, end_date))
        
        # Verify filter was called with correct parameters
        self.mock_queryset.filter.assert_called_with(
            news__date_published__range=(start_date, end_date)
        )
        
        # Verify filtered queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_apply_filters_with_ids_only(self):
        """Test apply_filters with ids_only=True flag"""
        # Call the method with ids_only flag
        result = self.filter_service.apply_filters(ids_only=True)
        
        # Verify values method was called
        self.mock_queryset.values.assert_called_with('id')
        
        # Verify values result was returned
        self.assertEqual(result, [{'id': 1}, {'id': 2}])
    
    def test_apply_filters_with_multiple_filters(self):
        """Test apply_filters with multiple filters"""
        # Call the method with multiple filters
        diseases = ["COVID-19"]
        provinces = ["DKI Jakarta"]
        date_range = ("2023-01-01", "2023-12-31")
        result = self.filter_service.apply_filters(
            diseases=diseases,
            provinces=provinces,
            date_range=date_range
        )
        
        # Verify filter was called for each parameter
        # The exact number of calls depends on implementation
        self.assertEqual(self.mock_queryset.filter.call_count, 3)
        
        # Verify filtered queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_filter_by_diseases(self):
        """Test the _filter_by_diseases method directly"""
        # Setup test
        diseases = ["COVID-19", "Dengue"]
        
        # Call the method directly
        self.filter_service._filter_by_diseases(self.mock_queryset, diseases)
        
        # Verify filter was called correctly
        self.mock_queryset.filter.assert_called_with(disease__name__in=diseases)
    
    def test_filter_by_provinces(self):
        """Test the _filter_by_provinces method directly"""
        # Setup test
        provinces = ["DKI Jakarta", "Jawa Barat"]
        
        # Call the method directly
        self.filter_service._filter_by_provinces(self.mock_queryset, provinces)
        
        # Verify filter was called correctly
        self.mock_queryset.filter.assert_called_with(location__province__in=provinces)
    
    def test_filter_by_cities(self):
        """Test the _filter_by_cities method directly"""
        # Setup test
        cities = ["Jakarta", "Bandung"]
        
        # Call the method directly
        self.filter_service._filter_by_cities(self.mock_queryset, cities)
        
        # Verify filter was called correctly
        self.mock_queryset.filter.assert_called_with(location__city__in=cities)
    
    def test_filter_by_news_portals(self):
        """Test the _filter_by_news_portals method directly"""
        # Setup test
        news_portals = ["Kompas", "Detik"]
        
        # Call the method directly
        self.filter_service._filter_by_news_portals(self.mock_queryset, news_portals)
        
        # Verify filter was called correctly
        self.mock_queryset.filter.assert_called_with(news__portal__in=news_portals)
    
    def test_filter_by_status(self):
        """Test the _filter_by_status method directly"""
        # Setup test
        status = ["Biasa", "Waspada"]
        
        # Call the method directly
        self.filter_service._filter_by_status(self.mock_queryset, status)
        
        # Verify filter was called correctly
        self.mock_queryset.filter.assert_called_with(status__in=status)
    
    def test_filter_by_news_date_range(self):
        """Test the _filter_by_news_date_range method directly"""
        # Setup test
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        # Call the method directly
        self.filter_service._filter_by_news_date_range(self.mock_queryset, (start_date, end_date))
        
        # Verify filter was called correctly
        self.mock_queryset.filter.assert_called_with(
            news__date_published__range=(start_date, end_date)
        )
    
    def test_filter_by_news_date_range_invalid(self):
        """Test the _filter_by_news_date_range method with invalid input"""
        # Setup test with empty tuple
        date_range = ()
        
        # Call the method directly
        result = self.filter_service._filter_by_news_date_range(self.mock_queryset, date_range)
        
        # Verify filter was not called
        self.mock_queryset.filter.assert_not_called()
        
        # Verify original queryset was returned
        self.assertEqual(result, self.mock_queryset)
        
        # Test with None
        result = self.filter_service._filter_by_news_date_range(self.mock_queryset, None)
        self.assertEqual(result, self.mock_queryset)