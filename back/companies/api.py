import datetime
import time

import requests
from django.conf import settings
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import CorporateDisclosure
# Use the official OpenDART HTTPS endpoint
URL = 'https://opendart.fss.or.kr/api/list.json'


_SESSION = None


def _get_session():
    """Shared requests.Session with sane retries for flaky external API calls."""
    global _SESSION
    if _SESSION is not None:
        return _SESSION

    s = requests.Session()
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        status=5,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    s.mount('https://', adapter)
    s.mount('http://', adapter)
    _SESSION = s
    return _SESSION


def _get_dart_api_key():
    # Prefer per-process override via env var, then fallback to Django settings
    return os.environ.get('DART_API_KEY') or getattr(settings, 'DART_API_KEY', None)


def _parse_yyyymmdd(s):
    if not s:
        return None
    try:
        return datetime.datetime.strptime(str(s), '%Y%m%d').date()
    except Exception:
        return None


def get_all_corporate_disclosure_data(start_date, end_date):
    """
    전체 기업에 대해 DART API 호출하여 공시 데이터를 DB에 저장합니다.
    :param start_date: 시작일 (YYYYMMDD)
    :param end_date: 종료일 (YYYYMMDD)
    """
    page_count = 100  # increase page size to reduce number of requests
    page_num = 1     # 페이지 번호

    session = _get_session()
    headers = {'User-Agent': 'SSAFY-ESG-Project/1.0'}

    while True:
        params = {
            'crtfc_key': _get_dart_api_key(),
            'corp_code': '',
            'bgn_de': start_date,
            'end_de': end_date,
            'page_count': page_count,
            'page_no': page_num,
        }

        try:
            response = session.get(URL, params=params, headers=headers, timeout=(5, 30))
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
                disclosure_date = _parse_yyyymmdd(item.get('rcept_dt')) or item.get('disclosure_date')
                disclosure = CorporateDisclosure(
                    corp_name=item.get('corp_name') or item.get('corpName'),
                    disclosure_date=disclosure_date,
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
    :param corp_name: 기업명 또는 corp_code(8자리)
    :param start_date: 시작일 (YYYYMMDD)
    :param end_date: 종료일 (YYYYMMDD)
    :return: JSON 형태의 공시 데이터
    """
    params = {
        'crtfc_key': _get_dart_api_key(),  # API 키
        'bgn_de': start_date,       # 시작일
        'end_de': end_date,         # 종료일
        'page_count': 10,           # 페이지당 공시 건수
    }

    # DART list API supports both corp_name and corp_code.
    corp = corp_name
    if isinstance(corp, str) and corp.isdigit() and len(corp) == 8:
        params['corp_code'] = corp
    else:
        params['corp_name'] = corp

    session = _get_session()
    headers = {'User-Agent': 'SSAFY-ESG-Project/1.0'}

    try:
        response = session.get(URL, params=params, headers=headers, timeout=(5, 30))
    except requests.exceptions.RequestException as e:
        return {'error': f'Request failed: {e}'}

    if response.status_code != 200:
        return {'error': f'Failed to fetch data (status={response.status_code})', 'body': response.text[:500]}

    try:
        return response.json()
    except ValueError:
        return {'error': 'Invalid JSON from DART', 'body': response.text[:500]}


# Backwards-compatible wrappers (some modules expect these old names)
def fetch_disclosures_for_company(corp_name, start_date, end_date):
    """Compatibility wrapper for older callers."""
    return get_corporate_disclosure_data(corp_name, start_date, end_date)


def find_corp_code_by_name(corp_name):
    """Simple stub for compatibility. Returns None — implement lookup if needed."""
    return None