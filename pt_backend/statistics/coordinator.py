from pt_backend.statistics.factory import ReportFactory
from pt_backend.statistics.reports.prevalence import PrevalenceStatistics

class StatisticsCoordinator:
    def __init__(self, case_filter_service, cache_service=None):
        self.case_filter_service = case_filter_service
        self.strategies = ReportFactory.get_all()
        self.cache_service = cache_service

    def generate_comprehensive_report(self, **filters):
        # Only attempt caching if cache_service exists
        cache_key = None
        if self.cache_service:
            try:
                # Convert filter items to something hashable
                hashable_items = []
                for k, v in filters.items():
                    if isinstance(v, list):
                        v = tuple(v)  # Convert lists to tuples (which are hashable)
                    elif isinstance(v, dict):
                        # Convert nested dictionaries to tuples of tuples
                        v = tuple((k2, tuple(v2) if isinstance(v2, list) else v2) 
                                 for k2, v2 in v.items())
                    hashable_items.append((k, v))
                
                cache_key = f"stats_report_{hash(frozenset(hashable_items))}"
                cached_result = self.cache_service.get(cache_key)
                if cached_result:
                    return cached_result
            except Exception as e:
                # If caching fails, log it but continue without caching
                print(f"Caching error in statistics: {str(e)}")

        try:
            if self.case_filter_service:
                filtered = self.case_filter_service.filter_cases(**filters)
            else:
                filtered = []
        except Exception as e:
            return {"error": f"Failed to filter cases: {e}"}

        date_range = filters.get('date_range', {})
        start_date = date_range.get('start') if date_range else None

        out = {}
        for name, strategy in self.strategies.items():
            try:
                if isinstance(strategy, PrevalenceStatistics):
                    # Special case for PrevalenceStatistics
                    out[name] = strategy.generate_report(start_date=start_date)
                else:
                    # Strategy is expected to accept filtered_cases arg
                    out[name] = strategy.generate_report(filtered_cases=filtered)
            except Exception as e:
                out[name] = {"error": f"Failed to generate report: {e}"}

        # Cache the result if caching is available
        if self.cache_service and cache_key:
            try:
                self.cache_service.set(cache_key, out, timeout=3600)  # Cache for 1 hour
            except Exception as e:
                print(f"Error caching statistics result: {str(e)}")
                
        return out