from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('recommend/', views.get_company_recommendations, name='get_company_recommendations'),
    path('parse/', views.fetch_and_save_all_data),
    path('api/recommend/', api_views.RecommendCompanies.as_view(), name='api_recommend_companies'),
]
