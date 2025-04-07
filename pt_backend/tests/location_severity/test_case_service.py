from django.test import TestCase
from unittest.mock import MagicMock, patch
from pt_backend.services import CaseService
from pt_backend.models import Case
import uuid

class CaseServiceTestCase(TestCase):
    def setUp(self):
        # Create mock repository and cache service
        self.mock_repository = MagicMock()
        self.mock_cache_service = MagicMock()
        
        # Create the service with mocks
        self.service = CaseService(
            repository=self.mock_repository,
            cache_service=self.mock_cache_service
        )
        
        # Sample case data for testing
        self.sample_cases = [
            {"id": str(uuid.uuid4()), "disease__name": "COVID-19"},
            {"id": str(uuid.uuid4()), "disease__name": "Dengue"}
        ]
    
    def test_get_all_case_from_cache(self):
        """Test retrieving case data when it's in the cache"""
        # Setup cache to return data
        self.mock_cache_service.get.return_value = self.sample_cases
        
        # Call the method
        result = self.service.get_all_case()
        
        # Verify cache was checked with correct key
        self.mock_cache_service.get.assert_called_once_with(self.service.CACHE_KEY)
        
        # Verify repository was not called
        self.mock_repository.get_all_cases.assert_not_called()
        
        # Verify correct data was returned
        self.assertEqual(result, self.sample_cases)
    
    def test_get_all_case_from_repository(self):
        """Test retrieving case data when it's not in the cache"""
        # Setup cache to return None (cache miss)
        self.mock_cache_service.get.return_value = None
        
        # Setup repository to return data
        self.mock_repository.get_all_cases.return_value = self.sample_cases
        
        # Call the method
        result = self.service.get_all_case()
        
        # Verify cache was checked
        self.mock_cache_service.get.assert_called_once_with(self.service.CACHE_KEY)
        
        # Verify repository was called
        self.mock_repository.get_all_cases.assert_called_once()
        
        # Verify data was stored in cache
        self.mock_cache_service.set.assert_called_once_with(
            self.service.CACHE_KEY, 
            self.sample_cases, 
            timeout=self.service.CACHE_TIMEOUT
        )
        
        # Verify correct data was returned
        self.assertEqual(result, self.sample_cases)
    
    def test_get_all_case_empty_result(self):
        """Test handling empty result from repository"""
        # Setup cache to return None (cache miss)
        self.mock_cache_service.get.return_value = None
        
        # Setup repository to return None
        self.mock_repository.get_all_cases.return_value = None
        
        # Call the method
        result = self.service.get_all_case()
        
        # Verify empty list is returned
        self.assertEqual(result, [])