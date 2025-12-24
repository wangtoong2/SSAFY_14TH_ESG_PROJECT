from django.urls import path
from . import api_views

urlpatterns = [
    path('recommend/', api_views.UserCompanyRecommendations.as_view(), name='get_company_recommendations'),
    path('parse/', api_views.ParseCorporateDisclosures.as_view(), name='parse_corporate_disclosures'),
    path('api/recommend/', api_views.RecommendCompanies.as_view(), name='api_recommend_companies'),
    path('api/gpt_recommend/', api_views.GPTRecommendCompanies.as_view(), name='api_gpt_recommend_companies'),
    path('api/list/', api_views.CompanyList.as_view(), name='api_company_list'),
    path('api/companyprofile/summary/', api_views.CompanyProfileSummary.as_view(), name='api_companyprofile_summary'),
    # company comments
    path('api/<int:company_pk>/comments/', api_views.company_comment_list_create),
    path('api/comments/<int:comment_pk>/', api_views.company_comment_delete),
    path('api/comments/<int:comment_pk>/update/', api_views.company_comment_update),
    path('api/comments/<int:comment_pk>/like/', api_views.company_comment_like_toggle),
    path('api/<int:company_pk>/favorite/', api_views.company_favorite),
    path('api/myfavorites/', api_views.my_favorites),
]
