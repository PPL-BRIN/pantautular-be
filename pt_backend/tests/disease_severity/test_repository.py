from django.test import TestCase
from pt_backend.models import Disease, Case, Location
from pt_backend.repositories import DiseaseRepository, get_entity_severity_stats
import uuid
from unittest.mock import patch, MagicMock

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
        self.disease3 = Disease.objects.create(
            id=uuid.uuid4(),
            name="Test Disease 3",
            level_of_alertness=4
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
        # print("\nRESULT: ")
        # for result in results:
        #     print(result)
        # print()
        
        # Check we got results for both diseases
        self.assertEqual(len(results), 3)
        
        # First result should be the disease with most cases (disease1 with 3 cases)
        self.assertEqual(results[0]["name"], "Test Disease 1")
        self.assertEqual(results[0]["total_cases"], 3)
        
        # Second result should be disease2 with 1 case
        self.assertEqual(results[1]["name"], "Test Disease 2")
        self.assertEqual(results[1]["total_cases"], 1)
        
        # Check detailed counts for disease1
        self.assertEqual(results[0]["severity_counts"]["hospitalisasi"], 1)
        self.assertEqual(results[0]["severity_counts"]["insiden"], 1)
        self.assertEqual(results[0]["severity_counts"]["mortalitas"], 1)
        
        # Check detailed counts for disease2
        self.assertEqual(results[1]["severity_counts"]["hospitalisasi"], 1)
        self.assertEqual(results[1]["severity_counts"]["insiden"], 0)
        self.assertEqual(results[1]["severity_counts"]["mortalitas"], 0)

    def test_get_disease_severity_stats_limit(self):
        """Test that only top 12 diseases are returned"""
        # Create 15 more diseases with 1 case each
        for i in range(15):
            disease = Disease.objects.create(
                id=uuid.uuid4(),
                name=f"Extra Disease {i}",
                level_of_alertness=1
            )
            
            Case.objects.create(
                id=uuid.uuid4(),
                gender="male",
                age=30,
                city="Test City",
                status="minimal",
                severity="hospitalisasi",
                disease=disease,
                location=self.location1
            )
        
        # We should now have 17 diseases total (2 original + 15 new)
        results = self.repository.get_disease_severity_stats()
        # print("\nRESULT: ")
        # for result in results:
        #     print(result)
        # print()
        
        # Check that only 12 are returned
        self.assertEqual(len(results), 12)
        
        # First result should still be disease1 with 3 cases
        self.assertEqual(results[0]["name"], "Test Disease 1")
        self.assertEqual(results[0]["total_cases"], 3)

    def test_get_disease_severity_stats_error_handling(self):
        """Test error handling in the repository method"""
        # Update patch to match new implementation - patch annotate instead of prefetch_related
        with patch('django.db.models.query.QuerySet.annotate', 
                side_effect=Exception("Test exception")):
            result = self.repository.get_disease_severity_stats()
            
            # Check that we get an error dict back
            self.assertIsNotNone(result)
            self.assertIsInstance(result, dict)  # Should be a dict, not a list
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Error retrieving disease severity statistics")


# class TestDiseaseRepositoryWithFiltering(TestCase):
#     def setUp(self):
#         # Setup mock data
#         self.mock_disease = MagicMock(spec=Disease)
#         self.mock_disease.name = "COVID-19"
#         self.mock_disease.hospitalisasi_count = 10
#         self.mock_disease.insiden_count = 5
#         self.mock_disease.mortalitas_count = 2
#         self.mock_disease.total_cases = 17
        
#         self.repository = DiseaseRepository()
        
#     @patch('pt_backend.repositories.get_entity_severity_stats')
#     def test_get_disease_severity_stats_with_filter(self, mock_get_stats):
#         # Setup mock
#         mock_get_stats.return_value = [
#             {
#                 "name": "COVID-19",
#                 "severity_counts": {
#                     "hospitalisasi": 10,
#                     "insiden": 5,
#                     "mortalitas": 2
#                 },
#                 "total_cases": 17
#             }
#         ]
        
#         # Execute with filtered_case_ids
#         filtered_ids = [1, 2, 3]
#         result = self.repository.get_disease_severity_stats(filtered_case_ids=filtered_ids)
        
#         # Verify
#         mock_get_stats.assert_called_once_with(
#             model_class=Disease, 
#             group_by_field=None,
#             name_field="name", 
#             error_prefix="Error retrieving disease",
#             filtered_case_ids=filtered_ids
#         )
#         self.assertEqual(len(result), 1)
#         self.assertEqual(result[0]["name"], "COVID-19")