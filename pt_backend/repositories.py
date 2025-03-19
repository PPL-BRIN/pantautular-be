from .models import Case, Disease, Location, News
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from .models import Case
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
            diseases = Disease.objects.prefetch_related('cases')
            
            result = []
            for disease in diseases:
                # Initialize the disease info with only what's needed
                disease_info = {
                    "name": disease.name,
                    "severity_counts": {    
                        "hospitalisasi": 0,
                        "insiden": 0,
                        "mortalitas": 0
                    },
                    "total_cases": 0 
                }
                
                severity_counts = disease.cases.values('severity').annotate(count=Count('id'))
                
                # Fill in the counts and calculate total
                for item in severity_counts:
                    severity = item['severity'].lower()  # Normalize to lowercase
                    count = item['count']
                    
                    # Map any variations to standard keys
                    if severity == "insiden":
                        disease_info["severity_counts"]["insiden"] += count
                    elif severity == "hospitalisasi":
                        disease_info["severity_counts"]["hospitalisasi"] += count
                    elif severity == "mortalitas":
                        disease_info["severity_counts"]["mortalitas"] += count
                    
                    # Add to total regardless of severity type
                    disease_info["total_cases"] += count
                
                result.append(disease_info)
                
            return result
        except Exception as e:
            print(f"Repository ERROR: {str(e)}")
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
