from django.urls import path
from . import api_views

urlpatterns = [
    path('recommend/', api_views.UserCompanyRecommendations.as_view(), name='get_company_recommendations'),
    path('parse/', api_views.ParseCorporateDisclosures.as_view(), name='parse_corporate_disclosures'),
    path('api/recommend/', api_views.RecommendCompanies.as_view(), name='api_recommend_companies'),
    path('api/companyprofile/summary/', api_views.CompanyProfileSummary.as_view(), name='api_companyprofile_summary'),
]
