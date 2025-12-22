import datetime

from django.http import JsonResponse

from accounts.models import User
from .recommender import recommend_companies
from .api import get_all_corporate_disclosure_data

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

