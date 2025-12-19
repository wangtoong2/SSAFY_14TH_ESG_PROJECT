import requests
import os
from dotenv import load_dotenv
from django.db import models
from .models import CorporateDisclosure  # 모델 임포트 (다른 파일에 정의된 모델)

load_dotenv()

DART_API_KEY = os.getenv('DART_API_KEY')
URL = f'http://dart.fss.or.kr/api/search.json'


def get_all_corporate_disclosure_data(start_date, end_date):
    """
    전체 기업에 대해 DART API 호출하여 공시 데이터를 DB에 저장합니다.
    :param start_date: 시작일 (YYYYMMDD)
    :param end_date: 종료일 (YYYYMMDD)
    """
    page_count = 10  # 페이지당 공시 건수
    page_num = 1     # 페이지 번호

    while True:
        params = {
            'crtfc_key': DART_API_KEY,  # API 키
            'corp_name': '',             # 모든 기업 데이터
            'bgn_de': start_date,        # 시작일
            'end_de': end_date,          # 종료일
            'page_count': page_count,    # 페이지당 공시 건수
            'page_num': page_num        # 페이지 번호
        }

        # DART API 요청
        response = requests.get(URL, params=params)

        # 응답 상태 코드 확인
        if response.status_code == 200:
            print("Request was successful.")
            print("Response content:", response.text)  # 응답 내용을 출력하여 확인

            try:
                data = response.json()  # JSON 형식으로 응답을 파싱
            except requests.exceptions.JSONDecodeError:
                print("Error: Response is not in JSON format or empty response")
                break

            if not data.get('list'):  # 데이터가 없으면 종료
                print("No more data to fetch.")
                break

            # 데이터 처리 및 DB에 저장
            for item in data['list']:
                disclosure = CorporateDisclosure(
                    corp_name=item['corp_name'],
                    disclosure_date=item['disclosure_date'],
                    document_type=item['document_type'],
                    title=item['title'],
                    url=item['url']
                )
                disclosure.save()

            # 다음 페이지로 넘어가기
            page_num += 1
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            print("Response content:", response.text)  # 실패한 응답의 내용을 출력
            break

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