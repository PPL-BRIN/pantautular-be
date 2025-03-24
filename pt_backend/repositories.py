from .models import Case, Disease, Location, News
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from .interfaces import CaseRepositoryInterface

class DiseaseRepository:
    def get_all_diseases_name(self):
        try:
            diseases = Disease.objects.values_list("name", flat=True).distinct()
            if not diseases.exists():
                return []
            return list(diseases)
        except ObjectDoesNotExist:
            return {"error": "Error retrieving diseases"}

class LocationRepository:
    def get_all_locations_name(self):
        try:
            locations = Location.objects.values_list("city", flat=True).distinct()
            if not locations.exists():
                return []
            return list(locations)
        except ObjectDoesNotExist:
            return {"error": "Error retrieving locations"}
        

class NewsRepository:
    def get_all_news_name(self):
        try:
            news = News.objects.values_list("portal", flat=True).distinct()
            if not news.exists():
                return []
            return list(news)
        except ObjectDoesNotExist:
            return {"error": "Error retrieving news"}

    def get_top_five_local_portals(self):
        try:
            portals = News.objects.filter(
                type="Lokal"
            ).values('portal').annotate(
                count=Count('id')
            ).order_by('-count', 'portal')[:5]

            if not portals.exists():
                return []
            return portals
        except ObjectDoesNotExist:
            return {"error": "Error retrieving local portals"}

    def get_local_portal_statistics(self):
        try:
            # Get portals with news count and distinct disease count            
            portal_stats = News.objects.filter(
                type="Lokal"
            ).values(
                'portal'
            ).annotate(
                news_count=Count('id'),
                disease_count=Count('case__disease', distinct=True)
            ).order_by('-news_count')

            if not portal_stats.exists():
                return []

            return portal_stats
        except ObjectDoesNotExist:
            return {"error": "Error retrieving local portal statistics"}

class CaseRepository(CaseRepositoryInterface):
    def get_all_locations(self):
        return Case.get_all_locations()
