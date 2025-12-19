from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('recommend/', views.get_company_recommendations, name='get_company_recommendations'),
    path('parse/', views.fetch_and_save_all_data)
]
