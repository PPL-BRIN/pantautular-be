import datetime
from .repositories import DiseaseRepository, LocationRepository, CaseRepository
from .interfaces import CaseRetrievalInterface, CaseRepositoryInterface, CacheInterface
from django.core.cache import cache

class CaseService(CaseRetrievalInterface):
    CACHE_KEY = "all_case_locations"
    CACHE_TIMEOUT = 300 

    def __init__(self, repository: CaseRepositoryInterface, cache_service: CacheInterface):
        self.repository = repository
        self.cache_service = cache_service

    def get_all_case(self):
        cases = self.cache_service.get(self.CACHE_KEY)
        if cases is None:
            cases = self.repository.get_all_cases()
            self.cache_service.set(self.CACHE_KEY, cases, timeout=self.CACHE_TIMEOUT)
        return cases if cases else []

    def get_all_case_locations(self):
        locations = self.cache_service.get(self.CACHE_KEY)
        if locations is None:
            locations = self.repository.get_all_locations()
            self.cache_service.set(self.CACHE_KEY, locations, timeout=self.CACHE_TIMEOUT)
        return locations if locations else []

class CacheService(CacheInterface):
    def get(self, key):
        return cache.get(key)

    def set(self, key, value, timeout):
        cache.set(key, value, timeout)

    def delete(self, key):
        cache.delete(key)

class DiseaseService:
    def __init__(self, repository=None):
        self.repository = repository or DiseaseRepository()
    
    def get_disease_severity_stats(self):
        print("Service: Fetching disease severity stats")
        result = self.repository.get_disease_severity_stats()
        print(f"Service: Received result type: {type(result)}")
        return result

class LocationService:
    def __init__(self, repository=None):
        self.repository = repository or LocationRepository()
        
    def get_province_severity_stats(self):
        result = self.repository.get_province_severity_stats()
        return result

    def get_city_severity_stats(self):
        result = self.repository.get_city_severity_stats()
        return result
        
class CaseFilterService:
    """Service to handle filtering for severity statistics"""
    def __init__(self, case_service):
        self.case_service = case_service

    def apply_filters(self, 
                     diseases=None, 
                     provinces=None, 
                     cities=None, 
                     news_portals=None, 
                     alert_levels=None, 
                     date_range=None,
                     ids_only=False):
        result = self.case_service.get_all_case()
        result = self._filter_by_diseases(result, diseases)
        result = self._filter_by_provinces(result, provinces)
        result = self._filter_by_cities(result, cities)
        result = self._filter_by_news_portals(result, news_portals)
        result = self._filter_by_status(result, alert_levels)
        result = self._filter_by_news_date_range(result, date_range)
        if ids_only:
            return result.values('id')
        return result
    
    def _filter_by_diseases(self, cases, diseases):
        if diseases:
            return cases.filter(disease__name__in=diseases)
        return cases
    
    def _filter_by_provinces(self, cases, provinces):
        if provinces:
            return cases.filter(location__province__in=provinces)
        return cases

    def _filter_by_cities(self, cases, cities):
        if cities:
            return cases.filter(location__city__in=cities)
        return cases

    def _filter_by_news_portals(self, cases, news_portals):
        if news_portals:
            return cases.filter(news__portal__in=news_portals)
        return cases

    def _filter_by_status(self, cases, status):
        if status:
            return cases.filter(status__in=status)
        return cases

    def _filter_by_news_date_range(self, cases, news_date_range):
        if news_date_range and len(news_date_range) == 2:
            start_date, end_date = news_date_range
            return cases.filter(news__date_published__range=(start_date, end_date))
        return cases

class CasesSummaryFilterService:
    """Service to handle filtering for summary statistics"""
    def __init__(self):
        self.disease_repository = DiseaseRepository()
        self.location_repository = LocationRepository()
        self.filter_service = CaseFilterService(
            case_service=CaseService(
                repository=CaseRepository(), 
                cache_service=CacheService()
            )
        )
        
    def get_filter_stats(self, 
                          diseases=None, 
                          provinces=None, 
                          cities=None, 
                          news_portals=None, 
                          alert_levels=None, 
                          date_range=None):
        
        # Get filtered case IDs from filter service
        filtered_case_ids = self.filter_service.apply_filters(
            diseases, provinces, cities, news_portals, alert_levels, date_range, ids_only=True
        )
        
        # Get all three statistics using the same filtered case IDs
        return {
            "disease_stats": self.disease_repository.get_disease_severity_stats(filtered_case_ids),
            "province_stats": self.location_repository.get_province_severity_stats(filtered_case_ids),
            "city_stats": self.location_repository.get_city_severity_stats(filtered_case_ids)
        }