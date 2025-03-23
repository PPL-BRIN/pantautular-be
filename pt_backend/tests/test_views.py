from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from pt_backend.models import Case, Location, Disease
from pt_backend.services import CacheService, NewsService
import uuid
import os
from unittest.mock import patch, Mock


class CaseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.api_key = os.getenv("SECRET_API_KEY", "test-api-key")
        self.client.credentials(HTTP_X_API_KEY=self.api_key)

        self.disease1 = Disease.objects.create(name="Flu", level_of_alertness=2)
        self.disease2 = Disease.objects.create(name="COVID-19", level_of_alertness=5)
        self.location1 = Location.objects.create(latitude=-6.2088, longitude=106.8456, city="Jakarta")
        self.location2 = Location.objects.create(latitude=-6.9175, longitude=107.6191, city="Bandung")
        self.case1 = Case.objects.create(
            id=uuid.uuid4(), gender="Male", age=30, city="Jakarta", status="confirmed", disease=self.disease1, location=self.location1
        )
        self.case2 = Case.objects.create(
            id=uuid.uuid4(), gender="Female", age=25, city="Bandung", status="recovered", disease=self.disease2, location=self.location2
        )

        self.cache_service = CacheService()

    def test_get_all_case_locations(self):
        response = self.client.get('/cases/locations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data), 2)
        
        response_data.sort(key=lambda x: x['city'])
        expected_data = [
            {
                "id": str(self.case2.id),
                "location__longitude": "107.619100",
                "location__latitude": "-6.917500",
                "city": "Bandung"
            },
            {
                "id": str(self.case1.id),
                "location__longitude": "106.845600",
                "location__latitude": "-6.208800",
                "city": "Jakarta"
            }
        ]
        expected_data.sort(key=lambda x: x['city'])
        self.assertEqual(response_data, expected_data)

    def test_get_all_case_locations_empty(self):
        Case.objects.all().delete()
        self.cache_service.delete("all_case_locations")
        response = self.client.get('/cases/locations/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), {"error": "No case locations found"})

    @patch('pt_backend.services.CaseService.get_all_case_locations')
    def test_get_all_case_locations_exception(self, mock_get_all_locations):
        mock_get_all_locations.side_effect = Exception("Database error")
        response = self.client.get('/cases/locations/')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json(), {"error": "An unexpected error occurred. Please try again later."})

    def test_get_all_case_locations_missing_api_key(self):
        self.client.credentials()
        response = self.client.get('/cases/locations/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {"detail": "Invalid API Key"})

    def test_get_all_case_locations_invalid_api_key(self):
        self.client.credentials(HTTP_X_API_KEY="wrong-api-key")
        response = self.client.get('/cases/locations/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {"detail": "Invalid API Key"})


class CaseFilterPostTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.api_key = os.getenv("SECRET_API_KEY", "test-api-key")
        self.client.credentials(HTTP_X_API_KEY=self.api_key)
        
        self.patcher = patch('pt_backend.views.CaseFilterService')
        self.mock_filter_service = self.patcher.start()
        self.mock_filter_instance = Mock()
        self.mock_filter_service.return_value = self.mock_filter_instance

        self.test_uuid1 = uuid.uuid4()
        self.test_uuid2 = uuid.uuid4()

    def tearDown(self):
        self.patcher.stop()

    def test_post_filter_success(self):
        mock_cases = [
            {'id': str(self.test_uuid1), 'location__longitude': '106.845600', 'location__latitude': '-6.208800', 'city': 'Jakarta'},
            {'id': str(self.test_uuid2), 'location__longitude': '107.619100', 'location__latitude': '-6.917500', 'city': 'Bandung'}
        ]
        self.mock_filter_instance.filter_cases.return_value = mock_cases

        filter_data = {
            'diseases': ['COVID-19'],
            'locations': ['Jakarta']
        }
        response = self.client.post('/cases/locations/', filter_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mock_filter_instance.filter_cases.assert_called_once_with(filter_data)
        self.assertEqual(response.json(), mock_cases)

    def test_post_filter_no_results(self):
        self.mock_filter_instance.filter_cases.return_value = []
        response = self.client.post('/cases/locations/', {'diseases': ['Unknown']}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), {"error": "No case locations found matching the filters"})



    def test_post_filter_missing_api_key(self):
        self.client.credentials()
        response = self.client.post('/cases/locations/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {"detail": "Invalid API Key"})

    def test_post_filter_invalid_api_key(self):
        self.client.credentials(HTTP_X_API_KEY="wrong-api-key")
        response = self.client.post('/cases/locations/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {"detail": "Invalid API Key"})


class TopNationalPortalsViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.api_key = os.getenv("SECRET_API_KEY", "test-api-key")
        self.client.credentials(HTTP_X_API_KEY=self.api_key)
        
        # Setup mock repository and patch NewsService to use our mock
        self.patcher = patch('pt_backend.views.NewsService')
        self.mock_news_service = self.patcher.start()
        self.mock_service_instance = Mock()
        self.mock_news_service.return_value = self.mock_service_instance

    def tearDown(self):
        self.patcher.stop()

    def test_get_top_portals_success(self):
        # Mock data that would come from repository (through service)
        mock_data = [
            {"portal": "kompas.com", "count": 10},
            {"portal": "detik.com", "count": 8},
            {"portal": "tempo.co", "count": 6},
            {"portal": "cnn.com", "count": 4},
            {"portal": "republika.co.id", "count": 2}
        ]
        self.mock_service_instance.get_top_national_portals.return_value = mock_data

        # Make request
        response = self.client.get('/news/top-national-portals/')

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), mock_data)
        self.mock_service_instance.get_top_national_portals.assert_called_once()

    def test_get_top_portals_empty_result(self):
        # Mock empty result
        self.mock_service_instance.get_top_national_portals.return_value = []

        # Make request
        response = self.client.get('/news/top-national-portals/')

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_get_top_portals_repository_error(self):
        # Mock service error
        self.mock_service_instance.get_top_national_portals.side_effect = Exception("Database error")

        # Make request
        response = self.client.get('/news/top-national-portals/')

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json(), {"error": "An error occurred while fetching top portals"})

    def test_get_top_portals_error_response_from_repository(self):
        """Test handling of error response object from repository"""
        # Mock repository returning an error dictionary
        error_response = {"error": "Error retrieving national portals"}
        self.mock_service_instance.get_top_national_portals.return_value = error_response

        # Make request
        response = self.client.get('/news/top-national-portals/')

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json(), {"error": "An error occurred while fetching top portals"})

    def test_get_top_portals_queryset_conversion(self):
        """Test queryset conversion in view - covers views.py line 108"""
        # Create a mock queryset-like object
        class MockQuerySet:
            def __init__(self, data):
                self.data = data
            def values(self):
                return self.data
            def __iter__(self):
                return iter(self.data)
            def __bool__(self):
                return bool(self.data)
        
        # Create mock data with queryset-like behavior
        mock_data = MockQuerySet([
            {"portal": "kompas.com", "count": 10},
            {"portal": "detik.com", "count": 8}
        ])
        
        # Set return value with queryset-like object
        self.mock_service_instance.get_top_national_portals.return_value = mock_data
        
        # Make request
        response = self.client.get('/news/top-national-portals/')
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify the data was properly converted and serialized
        self.assertTrue(isinstance(response.json(), list))

    def test_news_service_exception_propagation(self):
        """Test service properly propagates exceptions to the view"""
        # Stop the existing patcher temporarily
        self.patcher.stop()
        
        try:
            # Test the actual NewsService class directly without mocking
            mock_repository = Mock()
            mock_repository.get_top_five_national_portals.side_effect = Exception("Repository error")
            
            # Test if the service correctly re-raises the exception
            with self.assertRaises(Exception):
                service = NewsService(mock_repository)
                service.get_top_national_portals()
        finally:
            # Restart the patcher for other tests
            self.mock_news_service = self.patcher.start()
            self.mock_service_instance = Mock()
            self.mock_news_service.return_value = self.mock_service_instance