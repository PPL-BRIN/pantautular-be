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
            # Extract filter parameters from request body
            data = request.data
            
            # Extract filter values, defaulting to None if not provided or empty
            diseases = data.get('diseases', []) or None
            
            # Handle locations by checking if the list exists and isn't empty
            locations = data.get('locations', [])
        
            # Get provinces for the specified cities in a single query
            provinces = None
            cities = None

            if locations:
                provinces = []
                cities = []
                
                # Check each location to determine if it's a province or a city
                for location in locations:
                    # Check if location is a province
                    province_exists = Location.objects.filter(province=location).exists()
                    if province_exists:
                        provinces.append(location)
                    
                    # Check if location is a city
                    city_exists = Location.objects.filter(city=location).exists()
                    if city_exists:
                        cities.append(location)
                        
                        # Add the associated province(s) for each city
                        city_provinces = Location.objects.filter(
                            city=location
                        ).values_list('province', flat=True).distinct()
                        provinces.extend(city_provinces)
                
                # Remove duplicates from provinces list
                if provinces:
                    provinces = list(set(provinces))
                else:
                    provinces = None
                    
                # Handle empty lists
                if not cities:
                    cities = None
            
            # Process other filters
            portals = data.get('portals', []) or None
            level_of_alertness = data.get('level_of_alertness') or None
            if level_of_alertness:
                level_of_alertness = int(level_of_alertness)
            
            # Handle date range
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            date_range = (start_date, end_date) if start_date or end_date else None
            
            # Initialize case summary filter service and get filtered stats
            cases_summary_filter = CasesSummaryFilterService()
            results = cases_summary_filter.get_filter_stats(
                diseases=diseases,
                provinces=provinces,
                cities=cities,
                news_portals=portals,
                alert_levels=level_of_alertness,
                date_range=date_range
            )
            
            return Response(results, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": f"Error processing filter request: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )