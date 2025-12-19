from .api import get_corporate_disclosure_data
from .models import CorporateDisclosure
from accounts.models import User

def recommend_companies(user_id):
    """
    사용자의 관심사 및 역량을 바탕으로 기업을 추천합니다.
    :param user_id: 사용자 ID
    :return: 추천된 기업 목록
    """
    user_profile = User.objects.get(user_id=user_id)
    interests = user_profile.interests.split(', ')  # 관심사 리스트로 분할

    recommended_companies = []

    for interest in interests:
        # 관심사에 맞는 기업 공시 데이터 검색
        companies_data = get_corporate_disclosure_data(interest, '20220101', '20221231')

        if 'list' in companies_data:
            for item in companies_data['list']:
                recommended_companies.append({
                    'corp_name': item['corp_name'],
                    'disclosure_date': item['disclosure_date'],
                    'title': item['title'],
                    'url': item['url']
                })

    return recommended_companies
