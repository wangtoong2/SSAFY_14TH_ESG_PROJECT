import datetime

from django.http import JsonResponse

from accounts.models import User
from .recommender import recommend_companies
from .api import get_all_corporate_disclosure_data
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Company

from companies.services import (
    recommend_companies,
    call_gpt_for_recommendations,
)

@api_view(["POST"])
def recommend_companies_api(request):
    """
    기업 추천 API
    """

    # =========================
    # 1. 입력값 파싱
    # =========================
    location = request.data.get("location")
    industry = request.data.get("industry")
    company_size = request.data.get("company_size")
    top_n = request.data.get("top_n", 5)

    # =========================
    # 2. 입력 검증 (필수)
    # =========================
    if not all([location, industry, company_size]):
        return Response(
            {"detail": "location, industry, company_size는 필수입니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        top_n = int(top_n)
        if top_n <= 0 or top_n > 20:
            raise ValueError
    except ValueError:
        return Response(
            {"detail": "top_n은 1~20 사이의 정수여야 합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # =========================
    # 3. 사용자 선호 prefs 구성
    # =========================
    prefs = {
        "location": location,
        "desired_industries": [industry],
        "desired_size": company_size,
    }

    # =========================
    # 4. 1차 로컬 추천 (필수)
    # =========================
def recommend_companies(prefs, top_n=20):
    """
    rule-based / DB 기반 추천
    """
    results = []

    for company in Company.objects.all():
        score = 0.0

        if company.location == prefs["location"]:
            score += 0.4
        if company.industry in prefs["desired_industries"]:
            score += 0.4
        if company.size == prefs["desired_size"]:
            score += 0.2

        if score > 0:
            results.append({
                "corp_name": company.name,
                "industry": company.industry,
                "size": company.size,
                "location": company.location,
                "score": round(score, 2),
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]


    # =========================
    # 5. GPT 재랭킹 (선택)
    # =========================
    try:
        result = call_gpt_for_recommendations(
            prefs=prefs,
            candidates=candidates,
            top_n=top_n,
        )
    except Exception as e:
        # GPT 실패 시 fallback
        result = candidates[:top_n]

    # =========================
    # 6. 응답 반환
    # =========================
    return Response(result, status=status.HTTP_200_OK)


def get_company_recommendations(request):
    """
    사용자의 관심사 및 역량에 맞는 기업을 추천합니다.
    :return: 추천된 기업 데이터
    """
    user_id = getattr(request.user, 'id', None)
    if not user_id:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    try:
        # 사용자 프로필 가져오기
        user_profile = User.objects.get(pk=user_id)
        # recommender.recommend_companies는 user_id만 받는다.
        _ = user_profile  # keep local reference
    except User.DoesNotExist:
        return JsonResponse({'error': 'User profile not found'}, status=400)

    recommended_companies = recommend_companies(user_id)
    return JsonResponse({'recommended_companies': recommended_companies})


def fetch_company_on_demand(request):
    """
    Endpoint to fetch disclosures for a single company on-demand.
    Query params: corp_name (required), start (YYYYMMDD, optional), end (YYYYMMDD, optional)
    """
    corp_name = request.GET.get('corp_name') or request.POST.get('corp_name')
    if not corp_name:
        return JsonResponse({'error': 'corp_name query parameter is required'}, status=400)

    start = request.GET.get('start') or request.POST.get('start')
    end = request.GET.get('end') or request.POST.get('end')
    # Legacy stub: 이 엔드포인트는 urls.py에서 더 이상 사용하지 않음
    return JsonResponse({'error': 'Deprecated endpoint'}, status=410)

def fetch_and_save_all_data(request):
    """
    전체 기업의 공시 데이터를 가져와 DB에 저장합니다.
    """
    start_date = '20220101'  # 예시: 시작일
    end_date = '20221215'    # 예시: 종료일

    # 전체 데이터 가져오기
    get_all_corporate_disclosure_data(start_date, end_date)

    return JsonResponse({'status': 'Data fetching and saving completed.'})


