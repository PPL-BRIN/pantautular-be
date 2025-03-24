from .models import Case, Disease, Location, News
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Case as DjangoCase, When, IntegerField, Sum, F
from .interfaces import CaseRepositoryInterface

def get_severity_stats(queryset, name_field, limit=12, error_prefix="Error retrieving"):
    """
    Generic helper to get severity statistics for any entity
    
    Args:
        queryset: Base queryset to annotate
        name_field: Field to use as the name in results
        limit: Max number of results to return
        error_prefix: Prefix for error messages
        
    Returns:
        List of dictionaries with severity stats or error dict
    """
    try:
        entities = queryset.annotate(
            name=F(name_field),
            hospitalisasi_count=Sum(
                DjangoCase(
                    When(severity__iexact='hospitalisasi', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            insiden_count=Sum(
                DjangoCase(
                    When(severity__iexact='insiden', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            mortalitas_count=Sum(
                DjangoCase(
                    When(severity__iexact='mortalitas', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            total_cases=Count('id')
        ).order_by('-total_cases')[:limit]
        
        # Format the response
        result = []
        for entity in entities:
            entity_info = {
                "name": entity['name'],
                "severity_counts": {
                    "hospitalisasi": entity['hospitalisasi_count'] or 0,
                    "insiden": entity['insiden_count'] or 0,
                    "mortalitas": entity['mortalitas_count'] or 0
                },
                "total_cases": entity['total_cases'] or 0
            }
            result.append(entity_info)
            
        return result
    except Exception:
        return {"error": f"{error_prefix} severity statistics"}

class DiseaseRepository:
    def get_all_diseases_name(self):
        try:
            diseases = Disease.objects.values_list("name", flat=True).distinct()
            if not diseases.exists():
                return []
            return list(diseases)
        except ObjectDoesNotExist:
            return {"error": "Error retrieving diseases"}
    
    def get_disease_severity_stats(self):
        # Customize query for Disease model
        base_query = Case.objects.values('disease__name')
        return get_severity_stats(
            queryset=base_query,
            name_field='disease__name',
            error_prefix="Error retrieving disease"
        )

class LocationRepository:
    def get_all_locations_name(self):
        try:
            locations = Location.objects.values_list("city", flat=True).distinct()
            if not locations.exists():
                return []
            return list(locations)
        except ObjectDoesNotExist:
            return {"error": "Error retrieving locations"}
    
    def get_province_severity_stats(self):
        # Customize query for provinces
        base_query = Case.objects.values('location__province')
        return get_severity_stats(
            queryset=base_query,
            name_field='location__province',
            error_prefix="Error retrieving province"
        )
    
    def get_city_severity_stats(self):
        # Customize query for cities
        base_query = Case.objects.values('location__city')
        return get_severity_stats(
            queryset=base_query, 
            name_field='location__city',
            error_prefix="Error retrieving city"
        )

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