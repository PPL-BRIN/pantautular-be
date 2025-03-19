from django.test import TestCase
from pt_backend.models import Disease, Case, Location
from pt_backend.repositories import DiseaseRepository
import uuid
from unittest.mock import patch

class DiseaseRepositoryTestCase(TestCase):
    def setUp(self):
        # Create test diseases
        self.disease1 = Disease.objects.create(
            id=uuid.uuid4(),
            name="Test Disease 1",
            level_of_alertness=3
        )
        self.disease2 = Disease.objects.create(
            id=uuid.uuid4(),
            name="Test Disease 2",
            level_of_alertness=2
        )
        
        # Create test locations
        self.location1 = Location.objects.create(
            id=uuid.uuid4(),
            latitude=0.0,
            longitude=0.0,
            city="Test Location 1",
            province="Test Province 1"
        )
        
        # Create test cases with various severities
        # Normal case with lowercase severity
        Case.objects.create(
            id=uuid.uuid4(),
            gender="male",
            age=30,
            city="Test City",
            status="minimal",
            severity="hospitalisasi",
            disease=self.disease1,
            location=self.location1
        )
        
        # Case with capitalized severity to test normalization
        Case.objects.create(
            id=uuid.uuid4(),
            gender="female",
            age=25,
            city="Test City",
            status="biasa",
            severity="Insiden",
            disease=self.disease1,
            location=self.location1
        )
        
        # Another case for same disease
        Case.objects.create(
            id=uuid.uuid4(),
            gender="male",
            age=40,
            city="Test City",
            status="bahaya",
            severity="mortalitas",
            disease=self.disease1,
            location=self.location1
        )
        
        # Case for second disease
        Case.objects.create(
            id=uuid.uuid4(),
            gender="female",
            age=35,
            city="Test City",
            status="katastropik",
            severity="hospitalisasi",
            disease=self.disease2,
            location=self.location1
        )
        
        self.repository = DiseaseRepository()

    def test_get_disease_severity_stats(self):
        """Test that disease severity stats are correctly calculated"""
        results = self.repository.get_disease_severity_stats()
        
        # Check we got results for both diseases
        self.assertEqual(len(results), 2)
        
        # Find each disease in results
        disease1_result = next((r for r in results if r["name"] == "Test Disease 1"), None)
        disease2_result = next((r for r in results if r["name"] == "Test Disease 2"), None)
        
        # Check disease1 stats
        self.assertIsNotNone(disease1_result)
        self.assertEqual(disease1_result["total_cases"], 3)
        self.assertEqual(disease1_result["severity_counts"]["hospitalisasi"], 1)
        self.assertEqual(disease1_result["severity_counts"]["insiden"], 1)  # Capitalized "Insiden" normalized
        self.assertEqual(disease1_result["severity_counts"]["mortalitas"], 1)
        
        # Check disease2 stats
        self.assertIsNotNone(disease2_result)
        self.assertEqual(disease2_result["total_cases"], 1)
        self.assertEqual(disease2_result["severity_counts"]["hospitalisasi"], 1)
        self.assertEqual(disease2_result["severity_counts"]["insiden"], 0)
        self.assertEqual(disease2_result["severity_counts"]["mortalitas"], 0)

    def test_get_disease_severity_stats_error_handling(self):
        """Test error handling in the repository method"""
        # Patch Disease.objects.prefetch_related to raise an exception
        with patch('pt_backend.models.Disease.objects.prefetch_related', 
                side_effect=Exception("Test exception")):
            result = self.repository.get_disease_severity_stats()
            
            # Check that we get an error dict back
            self.assertIsNotNone(result)
            self.assertIsInstance(result, dict)
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Error retrieving disease severity statistics")