from django.test import TestCase
from unittest.mock import MagicMock, Mock

from pt_backend.statistics.coordinator import StatisticsCoordinator


class TestStatisticsCoordinator(TestCase):
    def setUp(self):
        # mock CaseFilterService
        self.mock_filter = MagicMock()
        self.mock_filter.filter_cases.return_value = [{"foo": "bar"}]
        self.coord = StatisticsCoordinator(case_filter_service=self.mock_filter)

    def test_generate_all_reports(self):
        res = self.coord.generate_comprehensive_report()
        # pastikan memanggil filter_cases
        self.mock_filter.filter_cases.assert_called_once()
        # cek semua key strategy muncul
        expected_keys = [
            "prevalence_statistics",
            "age_statistics",
            "gender_statistics",
            "severity_statistics",
            "severity_dates_count_statistics",
            "national_news_statistics",
            "local_portal_statistics",
            "healthcare_news_statistics",
        ]
        for k in expected_keys:
            self.assertIn(k, res)
            self.assertIsInstance(res[k], dict)

    def test_filter_raises_exception(self):
        self.mock_filter.filter_cases.side_effect = Exception("fail")
        res = self.coord.generate_comprehensive_report()
        # kalau filter error, langsung return error di root
        self.assertIn("error", res)

    def test_single_strategy_raises(self):
        # buat salah satu strategy error
        self.coord.strategies["age_statistics"].generate_report = Mock(
            side_effect=Exception("oops")
        )
        out = self.coord.generate_comprehensive_report()
        # pastikan hanya age_statistics yang berisi error
        self.assertIn("error", out["age_statistics"])
        # strategy lain tetap ada
        self.assertIn("gender_statistics", out)
        self.assertNotIn("error", out.get("gender_statistics", {}))
    
    def test_no_filter_service_uses_empty_filtered_list(self):
        """Jika case_filter_service None, maka filtered_cases = []"""
        # buat coordinator tanpa filter service
        coord = StatisticsCoordinator(case_filter_service=None)
        # spy pada salah satu strategy untuk menangkap argumen
        strat = coord.strategies["age_statistics"]
        captured = []
        def fake_report(filtered_cases=None):
            captured.append(filtered_cases)
            return {"ok": True}

        strat.generate_report = fake_report

        out = coord.generate_comprehensive_report()
        # branch else harus mengeksekusi generate_report dengan []
        self.assertIn("age_statistics", out)
        self.assertEqual(captured, [[]])
        self.assertEqual(out["age_statistics"], {"ok": True})
    
    def test_caching_functionality(self):
        """Test that caching works correctly when cache_service is provided"""
        # Create a mock cache service
        mock_cache = MagicMock()
        mock_cache.get.return_value = None  # First call returns cache miss
        
        # Create coordinator with cache service
        coord_with_cache = StatisticsCoordinator(
            case_filter_service=self.mock_filter,
            cache_service=mock_cache
        )
        
        # First call should try to get from cache, miss, and then set cache
        result1 = coord_with_cache.generate_comprehensive_report(disease=["COVID-19"])
        
        # Verify cache interactions
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()
        
        # Reset mock call counts for next test
        mock_cache.get.reset_mock()
        mock_cache.set.reset_mock()
        
        # Set up mock to return cached result for second call
        cached_result = {"cached": "result"}
        mock_cache.get.return_value = cached_result
        
        # Second call with same params should get cache hit
        result2 = coord_with_cache.generate_comprehensive_report(disease=["COVID-19"])
        
        # Verify cache get was called but not set
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_not_called()
        
        # Result should be the cached value
        self.assertEqual(result2, cached_result)

    def test_cache_handles_unhashable_types(self):
        """Test that the coordinator correctly handles unhashable types in filters"""
        # Create mock cache service
        mock_cache = MagicMock()
        mock_cache.get.return_value = None
        
        # Create coordinator with cache service
        coord_with_cache = StatisticsCoordinator(
            case_filter_service=self.mock_filter,
            cache_service=mock_cache
        )
        
        # Call with complex filters containing lists and dicts
        complex_filters = {
            "diseases": ["COVID-19", "Dengue"],
            "locations": {
                "provinces": ["Jakarta", "Bali"],
                "cities": ["Jakarta Selatan"]
            }
        }
        
        # This should not raise an unhashable type error
        result = coord_with_cache.generate_comprehensive_report(**complex_filters)
        
        # Verify result is not an error
        self.assertNotIn("error", result)
        
        # Verify cache was attempted
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()

    def test_cache_get_exception_handled(self):
        """Test that exceptions during cache retrieval are properly handled"""
        # Create mock cache service that raises exception on get
        mock_cache = MagicMock()
        mock_cache.get.side_effect = Exception("Cache retrieval error")
        
        # Create coordinator with problematic cache service
        coord_with_cache = StatisticsCoordinator(
            case_filter_service=self.mock_filter,
            cache_service=mock_cache
        )
        
        # This should not raise an exception, the error should be caught
        try:
            result = coord_with_cache.generate_comprehensive_report(disease=["COVID-19"])
            
            # Verify cache get was attempted
            mock_cache.get.assert_called_once()
            
            # Coordinator should fall back to non-cached behavior
            self.mock_filter.filter_cases.assert_called_once()
            
            # We should still get a result, not an error
            self.assertTrue(isinstance(result, dict))
            self.assertNotIn("error", result)
        except Exception as e:
            self.fail(f"Exception was not properly handled: {str(e)}")

    def test_cache_set_exception_handled(self):
        """Test that exceptions during cache storage are properly handled"""
        # Create mock cache service that raises exception on set
        mock_cache = MagicMock()
        mock_cache.get.return_value = None  # Cache miss
        mock_cache.set.side_effect = Exception("Cache storage error")
        
        # Create coordinator with problematic cache service
        coord_with_cache = StatisticsCoordinator(
            case_filter_service=self.mock_filter,
            cache_service=mock_cache
        )
        
        # This should not raise an exception, the error should be caught
        try:
            result = coord_with_cache.generate_comprehensive_report(disease=["COVID-19"])
            
            # Verify both cache operations were attempted
            mock_cache.get.assert_called_once()
            mock_cache.set.assert_called_once()
            
            # We should still get a result, not an error
            self.assertTrue(isinstance(result, dict))
            self.assertNotIn("error", result)
        except Exception as e:
            self.fail(f"Exception was not properly handled: {str(e)}")