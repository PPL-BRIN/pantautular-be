import uuid
import random
from pt_backend.models import Disease, Location, Case

def generate_test_data(
    num_provinces=5, 
    cities_per_province=3, 
    cases_per_city=10, 
    disease=None
):
    """
    Generate test locations and cases for severity testing
    
    Args:
        num_provinces: Number of provinces to create
        cities_per_province: Number of cities to create per province
        cases_per_city: Number of cases to create per city
        disease: Disease instance to use (will create one if None)
    
    Returns:
        tuple: (test_disease, locations_dict, cases_list)
    """
    # Create a disease if not provided
    if not disease:
        disease = Disease.objects.create(
            id=uuid.uuid4(),
            name=f"Test Disease {uuid.uuid4().hex[:8]}",
            level_of_alertness=random.randint(1, 5)
        )
    
    # Define test data
    province_names = [
        "DKI Jakarta", "Jawa Barat", "Jawa Tengah", "Jawa Timur", "Sumatera Utara",
        "Sumatera Selatan", "Sulawesi Selatan", "Kalimantan Timur", "Bali", "Aceh",
        "Riau", "Lampung", "Banten", "DIY Yogyakarta", "Nusa Tenggara Barat"
    ]
    
    city_patterns = [
        "Kota {}", "Kabupaten {}", "{} Utara", "{} Selatan", "{} Timur", "{} Barat"
    ]
    
    city_names = [
        "Jakarta", "Bandung", "Surabaya", "Medan", "Makassar", "Semarang",
        "Palembang", "Tangerang", "Depok", "Padang", "Bekasi", "Malang",
        "Yogyakarta", "Bogor", "Solo", "Denpasar", "Balikpapan", "Manado",
        "Pontianak", "Banjarmasin", "Cirebon", "Samarinda", "Jambi", "Jayapura"
    ]
    
    statuses = ["minimal", "biasa", "bahaya", "katastropik"]
    severities = ["hospitalisasi", "insiden", "mortalitas"]
    genders = ["male", "female"]
    
    # Use a subset of provinces based on the requested number
    selected_provinces = random.sample(province_names, min(num_provinces, len(province_names)))
    
    locations = {}
    cases = []
    
    # Create locations and cases
    for province in selected_provinces:
        # Generate cities for this province
        province_cities = []
        for i in range(cities_per_province):
            if i < len(city_names):
                # Use predefined city names with patterns
                city_pattern = random.choice(city_patterns)
                city_base = city_names[i]
                city_name = city_pattern.format(city_base)
            else:
                # Generate numbered city names if we run out
                city_name = f"City {uuid.uuid4().hex[:6]}"
            
            province_cities.append(city_name)
        
        # Create location for each city
        for city in province_cities:
            # Create location with realistic coordinates
            # Indonesia roughly spans -11 to 6 latitude, 95 to 141 longitude
            latitude = random.uniform(-10, 6)
            longitude = random.uniform(95, 140)
            
            location = Location.objects.create(
                id=uuid.uuid4(),
                city=city,
                province=province,
                latitude=latitude,
                longitude=longitude
            )
            
            # Store created location
            if province not in locations:
                locations[province] = []
            locations[province].append(location)
            
            # Create cases for this location
            for _ in range(cases_per_city):
                # Create a case with random attributes
                case = Case.objects.create(
                    id=uuid.uuid4(),
                    gender=random.choice(genders),
                    age=random.randint(1, 90),
                    city=city,
                    status=random.choice(statuses),
                    # Weight the severities to make some more common
                    severity=random.choices(
                        severities, 
                        weights=[0.6, 0.3, 0.1], # hospitalisasi more common, mortalitas less common
                        k=1
                    )[0],
                    disease=disease,
                    location=location
                )
                cases.append(case)
    
    return disease, locations, cases

# Example usage:
# from pt_backend.tests.test_utils import generate_test_data
# disease, locations, cases = generate_test_data(num_provinces=5, cities_per_province=3, cases_per_city=10)