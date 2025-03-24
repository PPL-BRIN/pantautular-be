from django.urls import path
from .views import (
    AllCaseLocationsView, FiltersView, DiseaseSeverityStatsView,
    LocationSeverityStatsView, CitySeverityStatsView
)

urlpatterns = [
    path('cases/locations/', AllCaseLocationsView.as_view(), name='all-case-locations'),
    path('api/filters/', FiltersView.as_view(), name='filters'),
    path('api/diseases/severity-stats/', DiseaseSeverityStatsView.as_view(), name='disease-severity-stats'),
    path('api/locations/province/severity-stats/', LocationSeverityStatsView.as_view(), name='province-severity-stats'),
    path('api/locations/city/severity-stats/', CitySeverityStatsView.as_view(), name='city-severity-stats')
]
