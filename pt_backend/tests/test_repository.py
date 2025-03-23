from django.test import TestCase

from django.test import TestCase
from pt_backend.models import Case, Disease, Location, News
from pt_backend.repositories import DiseaseRepository, LocationRepository, NewsRepository, CaseRepository
from django.core.exceptions import ObjectDoesNotExist
import uuid
from unittest.mock import patch

class BaseTestCase(TestCase):
    def setUp(self):
        self.disease1 = Disease.objects.create(id=uuid.uuid4(), name="COVID-19", level_of_alertness=5)
        self.disease2 = Disease.objects.create(id=uuid.uuid4(), name="Ebola", level_of_alertness=4)

        self.location1 = Location.objects.create(id=uuid.uuid4(), latitude=-6.2088, longitude=106.8456, city="Jakarta")
        self.location2 = Location.objects.create(id=uuid.uuid4(), latitude=-6.9175, longitude=107.6191, city="Bandung")

        self.case1 = Case.objects.create(
            id=uuid.uuid4(), gender="Pria", age=30, city="Jakarta", status="kematian", disease=self.disease1, location=self.location1
        )
        self.case2 = Case.objects.create(
            id=uuid.uuid4(), gender="Wanita", age=25, city="Bandung", status="terjangkit", disease=self.disease2, location=self.location2
        )

        self.news1 = News.objects.create(
            id=uuid.uuid4(), portal="kompas.com", type="health", title="COVID-19 Detected in Jakarta", content="COVID-19 case detected in Jakarta...", url="https://www.kompas.com/covid-jakarta", author="Dr. Joko", case=self.case1
        )
        self.news2 = News.objects.create(
            id=uuid.uuid4(), portal="detik.com", type="health", title="SARS Detected in Medan", content="SARS case detected in Medan...", url="https://www.detik.com/sars-medan", author="Dr. Sari", case=self.case2
        )

class DiseaseRepositoryTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.repository = DiseaseRepository()

    def test_get_all_diseases_name(self):
        diseases = self.repository.get_all_diseases_name()
        expected = ["COVID-19", "Ebola"]
        for disease in diseases:
            self.assertIn(disease, expected)
        self.assertEqual(len(diseases), len(expected))

    def test_get_all_diseases_name_empty(self):
        Disease.objects.all().delete()  

        diseases = self.repository.get_all_diseases_name()
        self.assertEqual(diseases, [])

    @patch('pt_backend.models.Disease.objects.values_list', side_effect=ObjectDoesNotExist)
    def test_get_all_diseases_name_exception(self, mock_get_all_diseases):
        result = self.repository.get_all_diseases_name()
        self.assertEqual(result, {"error": "Error retrieving diseases"})

class LocationRepositoryTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.repository = LocationRepository()

    def test_get_all_locations_name(self):
        locations = self.repository.get_all_locations_name()
        expected = ["Jakarta", "Bandung"]
        for location in locations:
            self.assertIn(location, expected)
        self.assertEqual(len(locations), len(expected))

    def test_get_all_locations_name_empty(self):
        Location.objects.all().delete()  

        locations = self.repository.get_all_locations_name()
        self.assertEqual(locations, [])

    @patch('pt_backend.models.Location.objects.values_list', side_effect=ObjectDoesNotExist)
    def test_get_all_locations_name_exception(self, mock_get_all_locations):
        result = self.repository.get_all_locations_name()
        self.assertEqual(result, {"error": "Error retrieving locations"})

class NewsRepositoryTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.repository = NewsRepository()

    def test_get_all_news_name(self):
        news = self.repository.get_all_news_name()
        expected = ["kompas.com", "detik.com"]
        for news_item in news:
            self.assertIn(news_item, expected)
        self.assertEqual(len(news), len(expected))

    def test_get_all_news_name_empty(self):
        News.objects.all().delete()  

        news = self.repository.get_all_news_name()
        self.assertEqual(news, [])

    @patch('pt_backend.models.News.objects.values_list', side_effect=ObjectDoesNotExist)
    def test_get_all_news_name_exception(self, mock_get_all_news):
        result = self.repository.get_all_news_name()
        self.assertEqual(result, {"error": "Error retrieving news"})


class NewsRepositoryTopNationalPortalsTestCase(TestCase):
    def setUp(self):
        self.repository = NewsRepository()
        
        self.disease = Disease.objects.create(name="COVID-19", level_of_alertness=5)
        self.location = Location.objects.create(
            latitude=-6.9175, longitude=107.6191, city="Bandung"
        )
        self.case = Case.objects.create(
            id=uuid.uuid4(), gender="Pria", age=30, city="Jakarta", status="kematian", disease=self.disease, location=self.location
        )

        # Create 6 news objects
        self.news_national = [
            News.objects.create(
                id=uuid.uuid4(),
                portal="kompas.com",
                type="Nasional",
                title="News 1",
                content="Content 1",
                url="https://kompas.com/1",
                author="Author 1",
                case=self.case
            ),
            News.objects.create(
                id=uuid.uuid4(),
                portal="detik.com",
                type="Nasional",
                title="News 2",
                content="Content 2",
                url="https://detik.com/1",
                author="Author 2",
                case=self.case
            ),
            News.objects.create(
                id=uuid.uuid4(),
                portal="cnn.com",
                type="Nasional",
                title="News 3",
                content="Content 3",
                url="https://cnn.com/1",
                author="Author 3",
                case=self.case
            ),
            News.objects.create(
                id=uuid.uuid4(),
                portal="tempo.co",
                type="Nasional",
                title="News 4",
                content="Content 4",
                url="https://tempo.co/1",
                author="Author 4",
                case=self.case
            ),
            News.objects.create(
                id=uuid.uuid4(),
                portal="republika.co.id",
                type="Nasional",
                title="News 5",
                content="Content 5",
                url="https://republika.co.id/1",
                author="Author 5",
                case=self.case
            ),
            News.objects.create(
                id=uuid.uuid4(),
                portal="tribun.com",
                type="Nasional",
                title="News 6",
                content="Content 6",
                url="https://tribun.com/1",
                author="Author 6",
                case=self.case
            )
        ]

    def test_get_top_five_national_portals(self):
        top_portals = self.repository.get_top_five_national_portals()
        self.assertEqual(top_portals.count(), 5)

        portals = [item["portal"] for item in top_portals]
        self.assertEqual(len(portals), 5)

        for portal in top_portals:
            self.assertEqual(portal["count"], 1)

        self.assertNotIn("tribun.com", portals)

    def test_get_top_five_national_portals_empty(self):
        News.objects.all().delete()

        top_portals = self.repository.get_top_five_national_portals()
        self.assertEqual(top_portals, [])

    def test_get_top_five_national_portals_less_than_five(self):
        News.objects.filter(portal="tribun.com").delete()
        News.objects.filter(portal="republika.co.id").delete()

        top_portals = self.repository.get_top_five_national_portals()
        self.assertEqual(top_portals.count(), 4)

        portals = [item["portal"] for item in top_portals]
        self.assertEqual(len(portals), 4)

        for portal in top_portals:
            self.assertEqual(portal["count"], 1)

        self.assertNotIn("tribun.com", portals)
        self.assertNotIn("replubika.co.id", portals)

    @patch('pt_backend.models.News.objects.filter')
    def test_get_top_five_national_portals_object_does_not_exist(self, mock_filter):
        mock_filter.side_effect = ObjectDoesNotExist()
        
        result = self.repository.get_top_five_national_portals()
        
        self.assertEqual(
            result, 
            {"error": "Error retrieving national portals"}
        )
        
        mock_filter.assert_called_once_with(type="Nasional")

class NewsRepositoryNationalPortalStatisticsTestCase(TestCase):
    def setUp(self):
        self.repository = NewsRepository()
        
        # Create diseases
        self.disease1 = Disease.objects.create(name="COVID-19", level_of_alertness=5)
        self.disease2 = Disease.objects.create(name="Ebola", level_of_alertness=5)
        self.disease3 = Disease.objects.create(name="Malaria", level_of_alertness=4)
        
        # Create locations
        self.location = Location.objects.create(
            latitude=-6.9175, longitude=107.6191, city="Bandung", province="West Java"
        )
        
        # Create cases
        self.case1 = Case.objects.create(
            id=uuid.uuid4(), gender="Pria", age=30, city="Jakarta", 
            status="Bahaya", severity="hospitalisasi", disease=self.disease1, location=self.location
        )
        self.case2 = Case.objects.create(
            id=uuid.uuid4(), gender="Wanita", age=25, city="Surabaya", 
            status="Bahaya", severity="mortalitas", disease=self.disease2, location=self.location
        )
        self.case3 = Case.objects.create(
            id=uuid.uuid4(), gender="Pria", age=40, city="Bandung", 
            status="Biasa", severity="insiden", disease=self.disease3, location=self.location
        )
        
        # Create national news from different portals with various diseases
        self.news_kompas = [
            News.objects.create(
                portal="kompas.com", type="Nasional", title="News K1",
                content="Content K1", url="https://kompas.com/1", author="Author K1", case=self.case1
            ),
            News.objects.create(
                portal="kompas.com", type="Nasional", title="News K2",
                content="Content K2", url="https://kompas.com/2", author="Author K2", case=self.case1
            ),
            News.objects.create(
                portal="kompas.com", type="Nasional", title="News K3",
                content="Content K3", url="https://kompas.com/3", author="Author K3", case=self.case2
            )
        ]
        
        self.news_detik = [
            News.objects.create(
                portal="detik.com", type="Nasional", title="News D1",
                content="Content D1", url="https://detik.com/1", author="Author D1", case=self.case1
            ),
            News.objects.create(
                portal="detik.com", type="Nasional", title="News D2",
                content="Content D2", url="https://detik.com/2", author="Author D2", case=self.case2
            )
        ]
        
        self.news_cnn = [
            News.objects.create(
                portal="cnn.com", type="Nasional", title="News C1",
                content="Content C1", url="https://cnn.com/1", author="Author C1", case=self.case3
            )
        ]
        
        # Create non-national news (shouldn't be included in results)
        self.news_international = News.objects.create(
            portal="kompas.com", type="International", title="News Int",
            content="Content Int", url="https://kompas.com/int", author="Author Int", case=self.case1
        )

    def test_get_national_portal_statistics_success(self):
        # Get portal statistics
        portal_stats = self.repository.get_national_portal_statistics()
        
        # Convert to dictionary for easier testing
        stats_dict = {stat['portal']: stat for stat in portal_stats}
        
        # Verify kompas.com data
        self.assertIn('kompas.com', stats_dict)
        self.assertEqual(stats_dict['kompas.com']['news_count'], 3)
        self.assertEqual(stats_dict['kompas.com']['disease_count'], 2)  # COVID-19 and Ebola
        
        # Verify detik.com data
        self.assertIn('detik.com', stats_dict)
        self.assertEqual(stats_dict['detik.com']['news_count'], 2)
        self.assertEqual(stats_dict['detik.com']['disease_count'], 2)  # COVID-19 and Ebola
        
        # Verify cnn.com data
        self.assertIn('cnn.com', stats_dict)
        self.assertEqual(stats_dict['cnn.com']['news_count'], 1)
        self.assertEqual(stats_dict['cnn.com']['disease_count'], 1)  # Malaria
        
        # Verify ordering (by news_count descending)
        portals = [stat['portal'] for stat in portal_stats]
        self.assertEqual(portals, ['kompas.com', 'detik.com', 'cnn.com'])

    def test_get_national_portal_statistics_empty(self):
        # Delete all news
        News.objects.all().delete()
        
        # Get stats
        portal_stats = self.repository.get_national_portal_statistics()
        
        # Verify empty result
        self.assertEqual(portal_stats, [])

    def test_get_national_portal_statistics_only_international_news(self):
        # Delete all national news, leaving only international
        News.objects.filter(type="Nasional").delete()
        
        # Get stats
        portal_stats = self.repository.get_national_portal_statistics()
        
        # Verify empty result since we only have international news
        self.assertEqual(portal_stats, [])

    @patch('pt_backend.models.News.objects.filter')
    def test_get_national_portal_statistics_object_does_not_exist(self, mock_filter):
        # Mock to raise exception
        mock_filter.side_effect = ObjectDoesNotExist()
        
        # Call method
        result = self.repository.get_national_portal_statistics()
        
        # Verify error response
        self.assertEqual(
            result, 
            {"error": "Error retrieving national portal statistics"}
        )
        
        # Verify filter was called with correct parameter
        mock_filter.assert_called_once_with(type="Nasional")

class CaseRepositoryTestCase(TestCase):
    def setUp(self):
        self.disease = Disease.objects.create(name="COVID-19", level_of_alertness=5)
        self.location = Location.objects.create(
            latitude=-6.9175, longitude=107.6191, city="Bandung"
        )
        self.case = Case.objects.create(
            id=uuid.uuid4(),
            gender="Female",
            age=25,
            city="Bandung",
            status="recovered",
            disease=self.disease,
            location=self.location
        )
        self.repository = CaseRepository()

    def test_get_all_case_locations(self):
        locations = self.repository.get_all_locations()
        self.assertTrue(locations.exists())
        self.assertEqual(locations.count(), 1)
        case_data = locations.first()
        self.assertEqual(str(case_data["id"]), str(self.case.id))
        self.assertEqual(float(case_data["location__latitude"]), -6.9175)
        self.assertEqual(float(case_data["location__longitude"]), 107.6191)
        self.assertEqual(case_data["city"], "Bandung")

    def test_get_all_case_locations_empty(self):
        Case.objects.all().delete()
        locations = self.repository.get_all_locations()
        self.assertFalse(locations.exists())
