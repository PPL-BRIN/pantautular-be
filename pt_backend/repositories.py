from .models import Case, Disease, Location, News
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count,  Case as DjangoCase, When, IntegerField, Sum, F
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
            diseases = Disease.objects.annotate(
                hospitalisasi_count=Sum(
                    DjangoCase(
                        When(cases__severity__iexact='hospitalisasi', then=1),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                insiden_count=Sum(
                    DjangoCase(
                        When(cases__severity__iexact='insiden', then=1),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                mortalitas_count=Sum(
                    DjangoCase(
                        When(cases__severity__iexact='mortalitas', then=1),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                total_cases=Count('cases')
            ).order_by('-total_cases')[:12]
            
            # Format the response
            result = []
            for disease in diseases:
                disease_info = {
                    "name": disease.name,
                    "severity_counts": {
                        "hospitalisasi": disease.hospitalisasi_count or 0,
                        "insiden": disease.insiden_count or 0,
                        "mortalitas": disease.mortalitas_count or 0
                    },
                    "total_cases": disease.total_cases or 0
                }
                result.append(disease_info)
            return result
        
        except Exception:
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
            provinces = Case.objects.values('location__province').annotate(
                name=F('location__province'),  # Alias for consistent serialization
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
            ).order_by('-total_cases')[:12]
            
            # Format the response
            result = []
            for province in provinces:
                province_info = {
                    "name": province['name'],
                    "severity_counts": {
                        "hospitalisasi": province['hospitalisasi_count'] or 0,
                        "insiden": province['insiden_count'] or 0,
                        "mortalitas": province['mortalitas_count'] or 0
                    },
                    "total_cases": province['total_cases'] or 0
                }
                result.append(province_info)
                
            return result
        except Exception as e:
            return {"error": f"Error retrieving province severity statistics: {str(e)}"}
        
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
