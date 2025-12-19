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

def fetch_and_save_all_data(request):
    """
    전체 기업의 공시 데이터를 가져와 DB에 저장합니다.
    """
    start_date = '20220101'  # 예시: 시작일
    end_date = '20251215'    # 예시: 종료일

    # 전체 데이터 가져오기
    get_all_corporate_disclosure_data(start_date, end_date)

    return JsonResponse({'status': 'Data fetching and saving completed.'})

