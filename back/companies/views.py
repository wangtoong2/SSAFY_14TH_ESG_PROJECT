from django.http import JsonResponse
from .recommender import recommend_companies
from .api import get_corporate_disclosure_data
from accounts.models import User  # 사용자 프로필 모델

def get_company_recommendations(request):
    """
    사용자의 관심사 및 역량에 맞는 기업을 추천합니다.
    :return: 추천된 기업 데이터
    """
    user_id = request.user.id
    try:
        # 사용자 프로필 가져오기
        user_profile = User.objects.get(user_id=user_id)
        interests = user_profile.interests.split(', ')  # 관심사를 리스트로 변환
        skills = user_profile.skills.split(', ')  # 역량을 리스트로 변환
    except User.DoesNotExist:
        return JsonResponse({'error': 'User profile not found'}, status=400)

    recommended_companies = recommend_companies(interests, skills)

    # 기업 공시 데이터 가져오기
    companies_data = []
    for company in recommended_companies:
        # 각 추천된 기업에 대해 공시 데이터 가져오기
        corporate_data = get_corporate_disclosure_data(company['corp_name'], '20220101', '20221231')
        if 'list' in corporate_data:
            for item in corporate_data['list']:
                companies_data.append({
                    'corp_name': item['corp_name'],
                    'disclosure_date': item['disclosure_date'],
                    'document_type': item['document_type'],
                    'title': item['title'],
                    'url': item['url']
                })

    return JsonResponse({'recommended_companies': companies_data})

from django.http import JsonResponse
from .api import get_all_corporate_disclosure_data

from .api import fetch_disclosures_for_company, find_corp_code_by_name


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
    # default last 1 year if not provided
    if not end:
        end = datetime.today().strftime('%Y%m%d')
    if not start:
        start_dt = datetime.strptime(end, '%Y%m%d') - relativedelta(years=1)
        start = start_dt.strftime('%Y%m%d')

    # attempt fetch and save
    result = fetch_disclosures_for_company(corp_name, start, end)
    return JsonResponse(result)

def fetch_and_save_all_data(request):
    """
    전체 기업의 공시 데이터를 가져와 DB에 저장합니다.
    """
    start_date = '20220101'  # 예시: 시작일
    end_date = '20221215'    # 예시: 종료일

    # 전체 데이터 가져오기
    get_all_corporate_disclosure_data(start_date, end_date)

    return JsonResponse({'status': 'Data fetching and saving completed.'})

