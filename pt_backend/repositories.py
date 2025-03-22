from .models import Case, Disease, Location, News
from django.core.exceptions import ObjectDoesNotExist
from .models import Case
from .interfaces import CaseRepositoryInterface
from django.db.models import Count, Case as DbCase, When, IntegerField

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

class CaseRepository(CaseRepositoryInterface):
    def get_all_locations(self):
        return Case.get_all_locations()

    def count_cases_by_age_group(self):
        
        result = Case.objects.aggregate(
            under_12=Count(DbCase(When(age__lt=12, then=1), output_field=IntegerField())),
            age_12_25=Count(DbCase(When(age__gte=12, age__lte=25, then=1), output_field=IntegerField())),
            age_26_45=Count(DbCase(When(age__gte=26, age__lte=45, then=1), output_field=IntegerField())),
            above_45=Count(DbCase(When(age__gt=45, then=1), output_field=IntegerField()))
        )
        
        return result