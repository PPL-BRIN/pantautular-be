from .repositories import DiseaseRepository, LocationRepository
from .interfaces import CaseRetrievalInterface, CaseRepositoryInterface, CacheInterface
from django.core.cache import cache

class CaseService(CaseRetrievalInterface):
    CACHE_KEY = "all_case_locations"
    CACHE_TIMEOUT = 300 

    def __init__(self, repository: CaseRepositoryInterface, cache_service: CacheInterface):
        self.repository = repository
        self.cache_service = cache_service

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
        