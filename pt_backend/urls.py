from django.urls import path
from .views import AllCaseLocationsView, FiltersView, TopLocalPortalsView, LocalPortalStatisticsView, CaseDetailView

urlpatterns = [
    path('cases/locations/', AllCaseLocationsView.as_view(), name='all-case-locations'),
    path('api/filters/', FiltersView.as_view(), name='filters'),
    path('api/dashboard/top-local-portals/', TopLocalPortalsView.as_view(), name='top-local-portals'),
    path('api/dashboard/local-portal-stats/', LocalPortalStatisticsView.as_view(), name='local-portal-stats'),
    path('cases/<uuid:case_id>/', CaseDetailView.as_view(), name='case-detail'),
]

