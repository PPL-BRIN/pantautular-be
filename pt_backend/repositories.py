from .models import Case, Disease, Location, News
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Case as DjangoCase, When, IntegerField, Sum, F
from django.db.models.functions import Coalesce
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
    
    def get_disease_severity_stats(self):
        try:
            entities = Disease.objects.annotate(
                hospitalisasi_count=Coalesce(
                    Sum(
                        DjangoCase(
                            When(cases__severity__iexact='hospitalisasi', then=1),
                            default=0,
                            output_field=IntegerField()
                        )
                    ), 0
                ),
                insiden_count=Coalesce(
                    Sum(
                        DjangoCase(
                            When(cases__severity__iexact='insiden', then=1),
                            default=0,
                            output_field=IntegerField()
                        )
                    ), 0
                ),
                mortalitas_count=Coalesce(
                    Sum(
                        DjangoCase(
                            When(cases__severity__iexact='mortalitas', then=1),
                            default=0,
                            output_field=IntegerField()
                        )
                    ), 0
                ),
                total_cases=Coalesce(Count('cases', distinct=True), 0)
            ).order_by('-total_cases')[:12]  # Ensure ordering by total cases

            # Format the response
            result = []
            for entity in entities:
                entity_info = {
                    "name": entity.name,
                    "severity_counts": {
                        "hospitalisasi": entity.hospitalisasi_count or 0,
                        "insiden": entity.insiden_count or 0,
                        "mortalitas": entity.mortalitas_count or 0,
                    },
                    "total_cases": entity.total_cases or 0,
                }
                result.append(entity_info)
                
            return result
        except Exception as e:
            print(f"Error in get_disease_severity_stats: {e}")
            return {"error": "Error retrieving disease severity statistics"}

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
        try:
            entities = Location.objects.values('province').annotate(
                hospitalisasi_count=Coalesce(
                    Sum(
                        DjangoCase(
                            When(cases__severity__iexact='hospitalisasi', then=1),
                            default=0,
                            output_field=IntegerField()
                        )
                    ), 0
                ),
                insiden_count=Coalesce(
                    Sum(
                        DjangoCase(
                            When(cases__severity__iexact='insiden', then=1),
                            default=0,
                            output_field=IntegerField()
                        )
                    ), 0
                ),
                mortalitas_count=Coalesce(
                    Sum(
                        DjangoCase(
                            When(cases__severity__iexact='mortalitas', then=1),
                            default=0,
                            output_field=IntegerField()
                        )
                    ), 0
                ),
                total_cases=Coalesce(Count('cases', distinct=True), 0)
            ).order_by('-total_cases')[:12]  # Ensure ordering by total cases

            # Format the response
            result = []
            for entity in entities:
                entity_info = {
                    "name": entity['province'],
                    "severity_counts": {
                        "hospitalisasi": entity['hospitalisasi_count'] or 0,
                        "insiden": entity['insiden_count'] or 0,
                        "mortalitas": entity['mortalitas_count'] or 0,
                    },
                    "total_cases": entity['total_cases'] or 0,
                }
                result.append(entity_info)
                
            return result
        except Exception as e:
            print(f"Error in get_province_severity_stats: {e}")
            return {"error": "Error retrieving province severity statistics"}
    
    def get_city_severity_stats(self):
        try:
            entities = Location.objects.values('city').annotate(
                hospitalisasi_count=Coalesce(
                    Sum(
                        DjangoCase(
                            When(cases__severity__iexact='hospitalisasi', then=1),
                            default=0,
                            output_field=IntegerField()
                        )
                    ), 0
                ),
                insiden_count=Coalesce(
                    Sum(
                        DjangoCase(
                            When(cases__severity__iexact='insiden', then=1),
                            default=0,
                            output_field=IntegerField()
                        )
                    ), 0
                ),
                mortalitas_count=Coalesce(
                    Sum(
                        DjangoCase(
                            When(cases__severity__iexact='mortalitas', then=1),
                            default=0,
                            output_field=IntegerField()
                        )
                    ), 0
                ),
                total_cases=Coalesce(Count('cases', distinct=True), 0)
            ).order_by('-total_cases')[:12]  # Ensure ordering by total cases

            # Format the response
            result = []
            for entity in entities:
                entity_info = {
                    "name": entity['city'],
                    "severity_counts": {
                        "hospitalisasi": entity['hospitalisasi_count'] or 0,
                        "insiden": entity['insiden_count'] or 0,
                        "mortalitas": entity['mortalitas_count'] or 0,
                    },
                    "total_cases": entity['total_cases'] or 0,
                }
                result.append(entity_info)
                
            return result
        except Exception as e:
            print(f"Error in get_city_severity_stats: {e}")
            return {"error": "Error retrieving city severity statistics"}


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