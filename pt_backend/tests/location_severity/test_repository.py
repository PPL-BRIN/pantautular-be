from django.test import TestCase
from pt_backend.models import Disease, Case, Location
from pt_backend.repositories import LocationRepository
import uuid
from unittest.mock import patch
from django.db.models import Count

class LocationRepositoryTestCase(TestCase):
    def setUp(self):
        # Create test diseases
        self.disease1 = Disease.objects.create(
            id=uuid.uuid4(),
            name="Test Disease 1",
            level_of_alertness=3
        )
        
        # Create test locations - provinces
        self.location1 = Location.objects.create(
            id=uuid.uuid4(),
            latitude=0.0,
            longitude=0.0,
            city="Jakarta Pusat",
            province="DKI Jakarta"
        )
        
        self.location2 = Location.objects.create(
            id=uuid.uuid4(),
            latitude=1.0,
            longitude=1.0,
            city="Bandung",
            province="Jawa Barat"
        )
        
        self.location3 = Location.objects.create(
            id=uuid.uuid4(),
            latitude=2.0,
            longitude=2.0,
            city="Surabaya",
            province="Jawa Timur"
        )
        
        # Create test cases with various severities
        # Cases for DKI Jakarta
        Case.objects.create(
            id=uuid.uuid4(),
            gender="male",
            age=30,
            city="Jakarta Pusat",
            status="minimal",
            severity="hospitalisasi",
            disease=self.disease1,
            location=self.location1
        )
        
        Case.objects.create(
            id=uuid.uuid4(),
            gender="female",
            age=25,
            city="Jakarta Pusat",
            status="biasa",
            severity="Insiden",
            disease=self.disease1,
            location=self.location1
        )
        
        Case.objects.create(
            id=uuid.uuid4(),
            gender="male",
            age=40,
            city="Jakarta Pusat",
            status="bahaya",
            severity="mortalitas",
            disease=self.disease1,
            location=self.location1
        )
        
        # Cases for Jawa Barat
        Case.objects.create(
            id=uuid.uuid4(),
            gender="female",
            age=35,
            city="Bandung",
            status="katastropik",
            severity="hospitalisasi",
            disease=self.disease1,
            location=self.location2
        )
        
        self.repository = LocationRepository()

    # Updated test methods only (keep the setUp method as is)
def test_get_location_severity_stats(self):
    """Test retrieving location stats by province"""
    results = self.repository.get_location_severity_stats()
    
    # Check we got results for both provinces
    self.assertEqual(len(results), 2)
    
    # First result should be the province with most cases (DKI Jakarta with 3 cases)
    self.assertEqual(results[0]["name"], "DKI Jakarta")
    self.assertEqual(results[0]["total_cases"], 3)
    
    # Second result should be Jawa Barat with 1 case
    self.assertEqual(results[1]["name"], "Jawa Barat")
    self.assertEqual(results[1]["total_cases"], 1)
    
    # Check detailed counts for DKI Jakarta
    self.assertEqual(results[0]["severity_counts"]["hospitalisasi"], 1)
    self.assertEqual(results[0]["severity_counts"]["insiden"], 1)
    self.assertEqual(results[0]["severity_counts"]["mortalitas"], 1)
    
    # Check detailed counts for Jawa Barat
    self.assertEqual(results[1]["severity_counts"]["hospitalisasi"], 1)
    self.assertEqual(results[1]["severity_counts"]["insiden"], 0)
    self.assertEqual(results[1]["severity_counts"]["mortalitas"], 0)

def test_get_location_severity_stats_limit(self):
    """Test that only top 12 locations are returned"""
    # Create 15 more locations and cases
    # (keep the existing implementation)
    
    # Now we should have 17 locations total
    results = self.repository.get_location_severity_stats()
    
    # Check that only 12 are returned
    self.assertEqual(len(results), 12)
    
    # First result should still be DKI Jakarta with 3 cases
    self.assertEqual(results[0]["name"], "DKI Jakarta")
    self.assertEqual(results[0]["total_cases"], 3)

def test_get_location_severity_stats_error_handling(self):
    """Test error handling in the repository method"""
    with patch('django.db.models.query.QuerySet.values', 
            side_effect=Exception("Test exception")):
        result = self.repository.get_location_severity_stats()
        
        # Check that we get an error dict back
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertTrue(result["error"].startswith("Error retrieving location severity statistics"))