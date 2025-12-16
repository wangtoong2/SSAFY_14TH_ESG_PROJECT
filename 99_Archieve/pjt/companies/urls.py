from django.urls import path
from .views import (
    ImportCompanyAPIView,
    CompanyListAPIView,
    CompanyDetailAPIView,
)

urlpatterns = [
    # DART → DB 저장
    path('import/', ImportCompanyAPIView.as_view()),

    # 기업 목록 조회
    path('', CompanyListAPIView.as_view()),

    # 기업 상세 조회
    path('<str:corp_code>/', CompanyDetailAPIView.as_view()),
]
