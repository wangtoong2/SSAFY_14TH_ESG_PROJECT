import requests
import os
import time
from dotenv import load_dotenv
from django.db import models
from .models import CorporateDisclosure  # 모델 임포트 (다른 파일에 정의된 모델)

load_dotenv()

# prefer environment / Django settings for API key
DART_API_KEY = os.getenv('DART_API_KEY')
# Use the official OpenDART HTTPS endpoint
URL = 'https://opendart.fss.or.kr/api/list.json'


def get_all_corporate_disclosure_data(start_date, end_date):
    """
    전체 기업에 대해 DART API 호출하여 공시 데이터를 DB에 저장합니다.
    :param start_date: 시작일 (YYYYMMDD)
    :param end_date: 종료일 (YYYYMMDD)
    """
    page_count = 100  # increase page size to reduce number of requests
    page_num = 1     # 페이지 번호

    session = requests.Session()
    headers = {'User-Agent': 'SSAFY-ESG-Project/1.0 (+https://example.com)'}

    while True:
        params = {
            'crtfc_key': DART_API_KEY,
            'corp_code': '',
            'bgn_de': start_date,
            'end_de': end_date,
            'page_count': page_count,
            'page_no': page_num,
        }

        try:
            response = session.get(URL, params=params, headers=headers, timeout=30)
        except Exception as e:
            print(f"Request exception: {e}")
            break

        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            print(response.text[:1000])
            break

        # try parse JSON
        try:
            data = response.json()
        except ValueError:
            # empty or invalid JSON
            print("Error: Response is not valid JSON or empty")
            print("Response snippet:", response.text[:1000])
            break

        if not data.get('list'):
            print("No more data to fetch or empty 'list'.")
            break

        # 데이터 처리 및 DB에 저장
        for item in data['list']:
            try:
                disclosure = CorporateDisclosure(
                    corp_name=item.get('corp_name') or item.get('corpName'),
                    disclosure_date=item.get('rcept_dt') or item.get('disclosure_date'),
                    document_type=item.get('report_tp') or item.get('document_type'),
                    title=item.get('report_nm') or item.get('title'),
                    url=item.get('url')
                )
                disclosure.save()
            except Exception:
                # skip problematic items
                continue

        page_num += 1
        # be gentle with the API
        time.sleep(0.1)

    print("Data fetching and saving completed.")


def get_corporate_disclosure_data(corp_name, start_date, end_date):
    """
    단일 기업에 대해 DART API 호출하여 공시 데이터를 가져옵니다.
    :param corp_name: 기업명
    :param start_date: 시작일 (YYYYMMDD)
    :param end_date: 종료일 (YYYYMMDD)
    :return: JSON 형태의 공시 데이터
    """
    params = {
        'crtfc_key': DART_API_KEY,  # API 키
        'corp_name': corp_name,     # 조회할 기업명
        'bgn_de': start_date,       # 시작일
        'end_de': end_date,         # 종료일
        'page_count': 10,           # 페이지당 공시 건수
    }

    # DART API 요청
    response = requests.get(URL, params=params)

    if response.status_code == 200:
        return response.json()  # JSON 형태로 반환
    else:
        return {'error': 'Failed to fetch data'}


# Backwards-compatible wrappers (some modules expect these old names)
def fetch_disclosures_for_company(corp_name, start_date, end_date):
    """Compatibility wrapper for older callers."""
    return get_corporate_disclosure_data(corp_name, start_date, end_date)


def find_corp_code_by_name(corp_name):
    """Simple stub for compatibility. Returns None — implement lookup if needed."""
    return None