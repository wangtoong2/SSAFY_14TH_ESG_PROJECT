from .api import get_corporate_disclosure_data
from .models import CorporateDisclosure
from datetime import datetime

def save_data_periodically():
    """
    주기적으로 데이터를 가져와 저장하는 작업
    """
    corp_name = '삼성전자'
    start_date = (datetime.now().year - 1) * 10000 + 101  # 예시: 작년 1월 1일
    end_date = datetime.now().year * 10000 + 1231  # 예시: 올해 12월 31일

    data = get_corporate_disclosure_data(corp_name, start_date, end_date)

    if 'list' in data:
        for item in data['list']:
            disclosure = CorporateDisclosure(
                corp_name=item['corp_name'],
                disclosure_date=item['disclosure_date'],
                document_type=item['document_type'],
                title=item['title'],
                url=item['url']
            )
            disclosure.save()
