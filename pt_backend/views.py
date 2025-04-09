from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from pt_backend.models import Location
from .serializers import CaseLocationSerializer, DiseaseSeverityStatsSerializer, LocationSeverityStatsSerializer
from .services import LocationService, CaseFilterService, CasesSummaryFilterService
from .services import CacheService, CaseService, DiseaseService
from .filter.service import CaseFilterService
from .repositories import CaseRepository, DiseaseRepository, LocationRepository, NewsRepository
from .authentication import APIKeyAuthentication

INTERNAL_SERVER_ERR_MSG = "An unexpected error occurred. Please try again later."

class AllCaseLocationsView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []
    
    serializer_class = CaseLocationSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        cache_service = CacheService()
        repository = CaseRepository()
        self.service = CaseService(repository, cache_service)
        self.filter_service = CaseFilterService()

    def get(self, request):
        try:
            cases = self.service.get_all_case_locations()
            if not cases:
                return Response({"error": "No case locations found"}, status=status.HTTP_404_NOT_FOUND)
            serialized_data = self.serializer_class(cases, many=True).data
            return Response(serialized_data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"error": INTERNAL_SERVER_ERR_MSG}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        try:
            if not request.data or all(not v for v in request.data.values()):
                cases = self.service.get_all_case_locations()

            else: 
                cases = self.filter_service.filter_cases(request.data)

            if not cases:
                return Response(
                    {"error": "No case locations found matching the filters"},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                self.serializer_class(cases, many=True).data,
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": INTERNAL_SERVER_ERR_MSG},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FiltersView(APIView):
    def get(self, request):
        disease_repository = DiseaseRepository()
        location_repository = LocationRepository()
        news_repository = NewsRepository()
        try:
            diseases = [{"value": d, "label": d} for d in disease_repository.get_all_diseases_name()]
            locations = [{"value": l, "label": l} for l in location_repository.get_all_locations_name()]
            news = [{"value": n, "label": n} for n in news_repository.get_all_news_name()]

            response_data = {
                "data": {
                    "diseases": diseases,
                    "locations": locations,
                    "news": news
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DiseaseSeverityStatsView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []
    
    serializer_class = DiseaseSeverityStatsSerializer
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = DiseaseService()
    
    def get(self, request):
        try:
            stats = self.service.get_disease_severity_stats()
            
            if isinstance(stats, dict) and "error" in stats:
                return Response(stats, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            serialized_data = self.serializer_class(stats, many=True).data
            return Response({
                "data": serialized_data
            }, status=status.HTTP_200_OK)
            
        except Exception:
            return Response(
                {"error": INTERNAL_SERVER_ERR_MSG},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class LocationSeverityStatsView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []
    
    serializer_class = LocationSeverityStatsSerializer
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        repository = LocationRepository()
        self.service = LocationService(repository=repository)
    
    def get(self, request):
        try:
            stats = self.service.get_province_severity_stats()
            
            if isinstance(stats, dict) and "error" in stats:
                return Response(stats, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            serialized_data = self.serializer_class(stats, many=True).data
            return Response({
                "data": serialized_data
            }, status=status.HTTP_200_OK)
            
        except Exception:
            return Response(
                {"error": INTERNAL_SERVER_ERR_MSG},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class CitySeverityStatsView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []
    
    serializer_class = LocationSeverityStatsSerializer
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        repository = LocationRepository()
        self.service = LocationService(repository=repository)
    
    def get(self, request):
        try:
            stats = self.service.get_city_severity_stats()
            
            if isinstance(stats, dict) and "error" in stats:
                return Response(stats, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            serialized_data = self.serializer_class(stats, many=True).data
            return Response({
                "data": serialized_data
            }, status=status.HTTP_200_OK)
            
        except Exception:
            return Response(
                {"error": INTERNAL_SERVER_ERR_MSG},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CasesSummaryFilterStatsView(APIView):
    """
    API endpoint to provide filtered stats for all dashboard components
    """
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []
    
    def post(self, request):
        """Handle POST requests with JSON payload for filtering"""
        try:
            # Extract and process filter parameters
            filter_params = self._extract_filter_parameters(request.data)
            
            # Initialize service and get results
            cases_summary_filter = CasesSummaryFilterService()
            results = cases_summary_filter.get_filter_stats(**filter_params)
            
            return Response(results, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": f"Error processing filter request: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _extract_filter_parameters(self, data):
        """Extract and process filter parameters from request data"""
        # Extract basic filters
        diseases = data.get('diseases', []) or None
        locations = data.get('locations', [])
        portals = data.get('portals', []) or None
        
        # Process location data
        provinces, cities = self._process_location_data(locations)
        
        # Process alertness level
        level_of_alertness = data.get('level_of_alertness') or None
        if level_of_alertness:
            level_of_alertness = int(level_of_alertness)
        
        # Handle date range
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        date_range = (start_date, end_date) if start_date or end_date else None
        
        return {
            'diseases': diseases,
            'provinces': provinces,
            'cities': cities,
            'news_portals': portals,
            'alert_levels': level_of_alertness,
            'date_range': date_range
        }
    
    def _process_location_data(self, locations):
        """Process location data to extract provinces and cities"""
        if not locations:
            return None, None
            
        provinces = []
        cities = []
        
        for location in locations:
            # Check if location is a province
            if Location.objects.filter(province=location).exists():
                provinces.append(location)
                continue
            
            # Check if location is a city
            if Location.objects.filter(city=location).exists():
                cities.append(location)
                
                # Add the associated province(s) for each city
                city_provinces = Location.objects.filter(
                    city=location
                ).values_list('province', flat=True).distinct()
                provinces.extend(city_provinces)
        
        # Clean up results
        provinces = list(set(provinces)) if provinces else None
        cities = cities if cities else None
        
        return provinces, cities