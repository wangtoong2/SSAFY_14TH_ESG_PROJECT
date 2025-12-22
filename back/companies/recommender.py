from .api import get_corporate_disclosure_data
from .models import CorporateDisclosure
from accounts.models import User

def recommend_companies(user_id):
    """
    사용자의 관심사 및 역량을 바탕으로 기업을 추천합니다.
    :param user_id: 사용자 ID
    :return: 추천된 기업 목록
    """
    # accounts.User에는 user_id 필드가 없고 pk(id)를 사용한다.
    user_profile = User.objects.get(pk=user_id)
    interests = [s.strip() for s in (user_profile.interests or '').split(',') if s.strip()]

    recommended_companies = []

    for interest in interests:
        # 관심사에 맞는 기업 공시 데이터 검색
        companies_data = get_corporate_disclosure_data(interest, '20220101', '20221231')

        items = (companies_data or {}).get('list') or []
        for item in items:
            recommended_companies.append({
                'corp_name': item.get('corp_name') or item.get('corpName'),
                'disclosure_date': item.get('rcept_dt') or item.get('disclosure_date'),
                'title': item.get('report_nm') or item.get('title'),
                'url': item.get('url')
            })

    return recommended_companies
