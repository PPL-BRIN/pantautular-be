from django.urls import path
from .views import AllCaseLocationsView, FiltersView, CaseAgeDistributionView

urlpatterns = [
    path('cases/locations/', AllCaseLocationsView.as_view(), name='all-case-locations'),
    path('api/filters/', FiltersView.as_view(), name='filters'),
    path('cases/age-distribution/', CaseAgeDistributionView.as_view(), name='age-distribution'),
]
