from django.test import TestCase
from unittest.mock import patch, MagicMock
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
        result = self.filter_service.apply_filters(disease=diseases)
        
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
        result = self.filter_service.apply_filters(portals=news_portals)
        
        # Verify filter was called with correct parameters
        self.mock_queryset.filter.assert_called_with(news__portal__in=news_portals)
        
        # Verify filtered queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_apply_filters_with_alert_levels(self):
        """Test apply_filters with alert levels filter"""
        # Call the method with alert level filter
        alert_levels = 2
        result = self.filter_service.apply_filters(level_of_alertness=alert_levels)
        
        # Verify filter was called with correct parameters
        self.mock_queryset.filter.assert_called_with(disease__level_of_alertness=alert_levels)
        
        # Verify filtered queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_apply_filters_with_date_range_tuple(self):
        """Test apply_filters with date range tuple"""
        # Call the method with date range tuple
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        date_range = (start_date, end_date)
        result = self.filter_service.apply_filters(date_range=date_range)
        
        # Verify filter was called with correct parameters
        self.mock_queryset.filter.assert_called_with(
            news__date_published__range=[start_date, end_date]
        )
        
        # Verify filtered queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_apply_filters_with_date_range_dict(self):
        """Test apply_filters with date range dictionary"""
        # Call the method with date range dictionary
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        date_range = {'start': start_date, 'end': end_date}
        result = self.filter_service.apply_filters(date_range=date_range)
        
        # Verify filter was called with correct parameters
        self.mock_queryset.filter.assert_called_with(
            news__date_published__range=[start_date, end_date]
        )
        
        # Verify filtered queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_apply_filters_with_start_date_only(self):
        """Test apply_filters with only start date"""
        # Call the method with only start date
        start_date = "2023-01-01"
        date_range = (start_date, None)
        result = self.filter_service.apply_filters(date_range=date_range)
        
        # Verify filter was called with correct parameters
        self.mock_queryset.filter.assert_called_with(
            news__date_published__gte=start_date
        )
        
        # Verify filtered queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_apply_filters_with_end_date_only(self):
        """Test apply_filters with only end date"""
        # Call the method with only end date
        end_date = "2023-12-31"
        date_range = (None, end_date)
        result = self.filter_service.apply_filters(date_range=date_range)
        
        # Verify filter was called with correct parameters
        self.mock_queryset.filter.assert_called_with(
            news__date_published__lte=end_date
        )
        
        # Verify filtered queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_apply_filters_with_invalid_date_range(self):
        """Test apply_filters with invalid date range format"""
        # Call the method with invalid date range
        date_range = "2023-01-01 to 2023-12-31"  # Not tuple or dict
        result = self.filter_service.apply_filters(date_range=date_range)
        
        # Verify filter was not called
        self.mock_queryset.filter.assert_not_called()
        
        # Verify original queryset was returned
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
        cities = ["Jakarta"]
        news_portals = ["Kompas"]
        alert_levels = 3
        date_range = ("2023-01-01", "2023-12-31")
        
        result = self.filter_service.apply_filters(
            disease=diseases,
            provinces=provinces,
            cities=cities,
            portals=news_portals,
            level_of_alertness=alert_levels,
            date_range=date_range
        )
        
        # Verify each filter method was called
        # We can't check exact call order with mock_calls due to implementation details,
        # but we can check the filter was called for each parameter
        calls = self.mock_queryset.filter.call_args_list
        self.assertEqual(len(calls), 6)  # One call for each filter
        
        # Verify filtered queryset was returned
        self.assertEqual(result, self.mock_queryset)
    
    def test_filter_by_disease_none(self):
        """Test _filter_by_disease with None parameter"""
        result = self.filter_service._filter_by_disease(self.mock_queryset, None)
        self.mock_queryset.filter.assert_not_called()
        self.assertEqual(result, self.mock_queryset)
    
    def test_filter_by_provinces_empty_list(self):
        """Test _filter_by_provinces with empty list"""
        result = self.filter_service._filter_by_provinces(self.mock_queryset, [])
        self.mock_queryset.filter.assert_not_called()
        self.assertEqual(result, self.mock_queryset)
    
    def test_filter_by_news_date_range_empty_tuple(self):
        """Test _filter_by_news_date_range with empty tuple"""
        result = self.filter_service._filter_by_news_date_range(self.mock_queryset, ())
        self.mock_queryset.filter.assert_not_called()
        self.assertEqual(result, self.mock_queryset)