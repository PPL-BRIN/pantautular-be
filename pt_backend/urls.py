from django.urls import path
from .views import AllCaseLocationsView, FiltersView, DiseaseSeverityStatsView

urlpatterns = [
    path('cases/locations/', AllCaseLocationsView.as_view(), name='all-case-locations'),
    path('api/filters/', FiltersView.as_view(), name='filters'),
    path('api/diseases/severity-stats/', DiseaseSeverityStatsView.as_view(), name='disease-severity-stats'),
]
