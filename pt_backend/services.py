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
        result = self.repository.get_disease_severity_stats()
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
    def __init__(self, case_service):
        self.case_service = case_service

    def apply_filters(self, 
                     disease=None, 
                     provinces=None, 
                     cities=None, 
                     portals=None, 
                     level_of_alertness=None, 
                     date_range=None,
                     ids_only=False
                     ):
        cases = self.case_service.get_all_case()
        cases = self._filter_by_disease(cases, disease)
        cases = self._filter_by_provinces(cases, provinces)
        cases = self._filter_by_cities(cases, cities)
        cases = self._filter_by_news_portals(cases, portals)
        cases = self._filter_by_disease_alertness(cases, level_of_alertness)
        cases = self._filter_by_news_date_range(cases, date_range)
        if ids_only:
            return cases.values('id')
        return cases
    
    def _filter_by_disease(self, cases, disease):
        if disease:
            return cases.filter(disease__name__in=disease)
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

    def _filter_by_disease_alertness(self, cases, alertness):
        if alertness:
            return cases.filter(disease__level_of_alertness=alertness)
        return cases

    def _filter_by_news_date_range(self, cases, date_range):
        if not date_range:
            return cases
        
        # Handle both tuple and dict formats
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        elif isinstance(date_range, dict):
            start_date = date_range.get('start')
            end_date = date_range.get('end')
        else:
            return cases
        
        if start_date and end_date:
            # Both dates provided
            return cases.filter(news__date_published__range=[start_date, end_date])
        elif start_date:
            # Only start date provided
            return cases.filter(news__date_published__gte=start_date)
        elif end_date:
            # Only end date provided
            return cases.filter(news__date_published__lte=end_date)
        
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