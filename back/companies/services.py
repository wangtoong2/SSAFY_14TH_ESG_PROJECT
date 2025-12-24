import datetime
import json
import logging
import os
import time
import requests
from django.conf import settings
from .models import Company, CompanyProfile
from .api import get_corporate_disclosure_data
from .constants import KSIC_SECTION_MAP
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# =========================================================
# GPT Rerank Function (GMS API)
# =========================================================
def call_gpt_for_recommendations(prefs, candidates, top_n=5):
    """GPT를 사용해 기업 추천 재정렬"""
    # 환경 변수에서 GMS_KEY 로드
    api_key = os.getenv("GMS_KEY")
    assert api_key, "GMS_KEY 환경 변수가 설정되어 있지 않습니다."
    
    if not api_key:
        logger.error("GMS_KEY not found in environment variables")
        raise RuntimeError("GMS API key not configured. Please set GMS_KEY in .env file")
    
    # 상위 후보만 선택 (top_n * 3개)
    summaries = [
        {
            "company_id": c["company_id"],
            "corp_name": c["corp_name"],
            "company_size": c["company_size"],
            "score": round(c["score"], 2),
        }
        for c in candidates[: top_n * 3]
    ]

    # OpenAI 형식의 페이로드 (GMS는 OpenAI API와 호환)
    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {
                "role": "system",
                "content": "너는 취업 추천 시스템이다. 주어진 기업 목록을 취업 관점에서 재정렬하라. 반드시 JSON 배열만 반환하고, 각 항목은 {\"company_id\": 숫자, \"rank\": 숫자, \"reason\": \"문자열\"} 형식이어야 한다."
            },
            {
                "role": "user",
                "content": f"다음 기업 목록을 분석하고 상위 {top_n}개를 추천하라:\n\n{json.dumps(summaries, ensure_ascii=False, indent=2)}"
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.3
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }


    try:
        # 올바른 엔드포인트 사용
        response = requests.post(
            "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        logger.info(f"GMS Response Status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"GMS Error Response: {response.text}")
            raise RuntimeError(f"GMS Error {response.status_code}: {response.text}")

        data = response.json()
        
        # OpenAI 응답 형식에서 content 추출
        content = data["choices"][0]["message"]["content"]
        
        # JSON 파싱 (마크다운 코드 블록 제거 처리)
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        result = json.loads(content)
        
        # 결과 검증
        if not isinstance(result, list):
            raise ValueError("GPT response is not a list")
        
        return result[:top_n]
        
    except requests.exceptions.Timeout:
        logger.error("GMS API request timed out")
        raise RuntimeError("GMS API request timed out after 30 seconds")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise RuntimeError(f"GMS API request failed: {e}")
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"Failed to parse GMS response: {e}")
        raise RuntimeError(f"Invalid response format from GMS: {e}")


def extract_region_from_address(addr):
    if not addr:
        return None
    first = str(addr).strip().split()[0]
    mapping = {
        '서울': '서울특별시',
        '부산': '부산광역시',
        '대구': '대구광역시',
        '인천': '인천광역시',
        '광주': '광주광역시',
        '대전': '대전광역시',
        '울산': '울산광역시',
        '세종': '세종특별자치시',
        '제주': '제주특별자치도',
    }
    for k, v in mapping.items():
        if first.startswith(k):
            return v
    return first


def _dedupe_list_of_dicts(items, keys):
    seen, out = set(), []
    for it in items or []:
        k = tuple(it.get(x) for x in keys)
        if k in seen:
            continue
        seen.add(k)
        out.append(it)
    return out


# =========================================================
# DART / Company Data
# =========================================================
try:
    from OpenDartReader import OpenDartReader
except Exception:
    OpenDartReader = None


def fetch_company_data(corp_name, days=365):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)

    resp = get_corporate_disclosure_data(
        corp_name,
        start.strftime('%Y%m%d'),
        end.strftime('%Y%m%d')
    )

    result = {
        'corp_name': corp_name,
        'corp_code': None,
        'latest_disclosures': [],
        'financials': None,
        'company_overview': None,
        'company_size': None,
    }

    if not resp or 'error' in resp:
        return result

    items = _dedupe_list_of_dicts(resp.get('list', []), ['rcept_dt', 'report_nm'])
    result['latest_disclosures'] = items[:5]

    result['financials'] = fetch_financial_summary(corp_name)
    result['company_overview'] = fetch_company_overview(corp_name)
    result['company_size'] = classify_company_size(
        result['company_overview'].get('stock_code') if result['company_overview'] else None,
        result['financials']
    )
    return result


def fetch_financial_summary(corp, years=2):
    api_key = os.environ.get('DART_API_KEY') or getattr(settings, 'DART_API_KEY', None)
    if not OpenDartReader or not api_key:
        return None

    odr = OpenDartReader(api_key)
    current_year = datetime.date.today().year

    out = {'years': {}, 'revenue_growth': None}
    prev_rev = None

    for y in range(current_year - years, current_year):
        try:
            df = odr.finstate_all(corp, bsns_year=y, reprt_code='11011', fs_div='CFS')
        except Exception:
            continue

        if df is None or df.empty:
            continue

        row = df[df['account_nm'].str.contains('매출')]
        if row.empty:
            continue

        revenue = int(str(row.iloc[0]['thstrm_amount']).replace(',', ''))
        out['years'][str(y)] = {'revenue': revenue}

        if prev_rev:
            out['revenue_growth'] = (revenue - prev_rev) / prev_rev
        prev_rev = revenue

    return out


def fetch_company_overview(corp):
    api_key = os.environ.get('DART_API_KEY') or getattr(settings, 'DART_API_KEY', None)
    if not OpenDartReader or not api_key:
        return None

    odr = OpenDartReader(api_key)
    raw = odr.company(corp)

    return {
        'corp_name': raw.get('corp_name'),
        'corp_code': raw.get('corp_code'),
        'stock_code': raw.get('stock_code'),
        'industry': raw.get('induty'),
        'addr': raw.get('adres'),
        'region': extract_region_from_address(raw.get('adres')),
    }


def classify_company_size(stock_code, financials):
    if not financials or not financials.get('years'):
        return '중견' if stock_code else None

    latest_year = max(financials['years'].keys())
    revenue = financials['years'][latest_year]['revenue']

    if revenue >= 1_000_000_000_000:
        return '대기업'
    elif revenue >= 100_000_000_000:
        return '중견'
    return '중소'


# =========================================================
# Scoring
# =========================================================
def score_company_for_user(prefs, data):
    score = 0.0
    overview = data.get('company_overview') or {}

    if prefs.get('desired_size') == data.get('company_size'):
        score += 1.0
    # safe check: prefs.location may be None; avoid `None in <string>` TypeError
    pref_loc = prefs.get('location')
    region_str = (overview.get('region') or '')
    if pref_loc and isinstance(region_str, str) and pref_loc in region_str:
        score += 0.5
    if prefs.get('desired_industries'):
        for ind in prefs['desired_industries']:
            if ind.lower() in (overview.get('industry') or '').lower():
                score += 1.0

    return score


from django.core.exceptions import ObjectDoesNotExist

def recommend_companies(prefs, top_n=10):
    results = []

    qs = Company.objects.all()

    for c in qs.iterator():
        try:
            profile = c.profile
        except ObjectDoesNotExist:
            continue

        data = profile.data or {}

        if data.get('company_size') is None:
            try:
                data['company_size'] = classify_company_size(
                    c.stock_code, data.get('financials')
                )
            except Exception:
                data['company_size'] = None

        score = score_company_for_user(prefs, data)

        results.append({
            'company_id': c.id,
            'corp_name': c.corp_name,
            'company_size': data.get('company_size'),
            'score': score,
            'profile': data,
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_n]


def build_fixed_companyprofile_payload():
    pass