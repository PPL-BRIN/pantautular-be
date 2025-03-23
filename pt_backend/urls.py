from django.urls import path
from .views import AllCaseLocationsView, FiltersView, NationalPortalStatisticsView, TopNationalPortalsView

urlpatterns = [
    path('cases/locations/', AllCaseLocationsView.as_view(), name='all-case-locations'),
    path('api/filters/', FiltersView.as_view(), name='filters'),
    path('news/top-national-portals/', TopNationalPortalsView.as_view(), name='top-national-portals'),
    path('news/national-portal-stats/', NationalPortalStatisticsView.as_view(), name='national-portal-stats'),
]
