import datetime
import json
import logging
import os
import random
import time
import requests
from django.conf import settings
from .models import Company, CompanyProfile
from .api import get_corporate_disclosure_data
from .constants import KSIC_SECTION_MAP, KSIC_SECTION_RANGES
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# =========================================================
# GPT Rerank Function (GMS API)
# =========================================================
def call_gpt_for_recommendations(prefs, candidates, top_n=5):
    """GPT(GMS)를 사용해 기업 추천 재정렬 (JSON 파싱 안정화 버전)"""

    api_key = os.getenv("GMS_KEY")
    if not api_key:
        logger.error("GMS_KEY not found in environment variables")
        raise RuntimeError("GMS_KEY 환경 변수가 설정되어 있지 않습니다.")

    # 상위 후보만 선택 (top_n * 3개)
    summaries = [
        {
            "company_id": c["company_id"],
            "corp_name": c.get("corp_name"),
            "company_size": c.get("company_size"),
            "score": round(c.get("score", 0), 2),
        }
        for c in candidates[: top_n * 3]
    ]

    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "너는 취업 준비생을 위한 기업 추천 AI이다.\n"
                    "주어진 기업 목록을 취업 관점에서 재정렬하라.\n\n"
                    "⚠️ 절대 규칙 (위반 시 출력 무효):\n"
                    "1. 반드시 JSON 배열만 출력할 것.\n"
                    "2. 설명, 문장, 코드블록, 주석을 절대 포함하지 말 것.\n"
                    "3. 모든 문자열은 한 줄이어야 하며 줄바꿈(\\n, \\r)을 포함하지 말 것.\n"
                    "4. 문자열 내부에 큰따옴표(\")를 사용할 경우 반드시 escape(\\\")할 것.\n"
                    "5. 출력은 아래 스키마와 정확히 일치해야 한다.\n\n"
                    "출력 스키마:\n"
                    "[\n"
                    "  {\n"
                    "    \"company_id\": number,\n"
                    "    \"corp_name\": string,\n"
                    "    \"rank\": number,\n"
                    "    \"reason\": string\n"
                    "  }\n"
                    "]"
                )
            },
            {
                "role": "user",
                "content": (
                    f"다음 기업 목록을 분석하고 상위 {top_n}개를 추천하라:\n\n"
                    f"{json.dumps(summaries, ensure_ascii=False)}"
                )
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.3,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    try:
        response = requests.post(
            "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            logger.error("GMS Error Response: %s", response.text)
            raise RuntimeError(f"GMS Error {response.status_code}")

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # ===============================
        # 🔥 출력 전처리 (핵심)
        # ===============================
        raw = content.strip()

        # 1) 코드블록 제거
        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        # 2) 줄바꿈 제거 (JSON 문자열 안정화)
        raw = raw.replace("\r", " ").replace("\n", " ")

        # 3) JSON 배열만 강제로 추출
        if "[" in raw and "]" in raw:
            raw = raw[raw.find("[") : raw.rfind("]") + 1]

        # 4) JSON 파싱
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error("===== GPT RAW OUTPUT (PARSE FAILED) =====")
            logger.error(raw)
            logger.error("========================================")
            raise RuntimeError(f"GMS API failed: {e}")

        if not isinstance(result, list):
            raise RuntimeError("GPT response is not a JSON list")

        # ===============================
        # 후처리
        # ===============================
        seen = set()
        cleaned = []

        for item in result:
            if not isinstance(item, dict):
                continue

            cid = item.get("company_id")
            if cid and cid not in seen:
                seen.add(cid)
                cleaned.append(item)

            if len(cleaned) >= top_n:
                break

        # rank 강제 재정렬 (1, 2, 3, ...)
        for idx, item in enumerate(cleaned, start=1):
            item["rank"] = idx

        return cleaned

    except requests.exceptions.Timeout:
        logger.error("GMS API request timed out")
        raise RuntimeError("GMS API request timed out")

    except requests.exceptions.RequestException as e:
        logger.error("GMS API request error: %s", e)
        raise RuntimeError(f"GMS API failed: {e}")


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


def _as_str_list(v):
    if not v:
        return []
    if isinstance(v, (list, tuple, set)):
        return [str(x).strip() for x in v if str(x).strip()]
    return [s.strip() for s in str(v).split(',') if s.strip()]


def _ksic_major_section_from_code(industry_code):
    """Return KSIC major section label from an industry code.

    Uses only KSIC_SECTION_RANGES (major groups), not KSIC_SECTION_MAP.
    """
    if industry_code is None:
        return None

    s = str(industry_code).strip()
    if not s:
        return None

    digits = ''.join(ch for ch in s if ch.isdigit())
    if not digits:
        return None

    prefix = ('0' + digits) if len(digits) == 1 else digits[:2]
    try:
        code2 = int(prefix)
    except Exception:
        return None

    for start, end, label in KSIC_SECTION_RANGES:
        if start <= code2 <= end:
            return label
    return None


def _effective_company_size(data):
    overview = data.get('company_overview') or {}
    return data.get('company_size') or overview.get('company_size')


def _effective_region(data):
    overview = data.get('company_overview') or {}
    region = overview.get('region') or data.get('region')
    if region:
        return region
    addr = overview.get('addr')
    return extract_region_from_address(addr) if addr else None


def _effective_industry_code(data):
    overview = data.get('company_overview') or {}
    return overview.get('industry_code') or data.get('industry_code')


def _effective_industry_text(data):
    overview = data.get('company_overview') or {}
    return overview.get('industry') or data.get('industry') or ''


def _matches_industry_pref(desired, data):
    """Match desired industry against KSIC major section or free-text industry."""
    if not desired:
        return False

    desired_s = str(desired).strip()
    if not desired_s:
        return False

    # 1) KSIC major section label match
    major = _ksic_major_section_from_code(_effective_industry_code(data))
    if major and desired_s == major:
        return True

    # 2) Support range/prefix filters like "10-34" or "62"
    code2 = None
    ic = _effective_industry_code(data)
    if ic is not None:
        ic_digits = ''.join(ch for ch in str(ic) if ch.isdigit())
        if ic_digits:
            try:
                code2 = int((ic_digits[:2]).rjust(2, '0'))
            except Exception:
                code2 = None

    if '-' in desired_s and code2 is not None:
        parts = [p.strip() for p in desired_s.split('-', 1)]
        try:
            start = int(''.join(ch for ch in parts[0] if ch.isdigit()))
            end = int(''.join(ch for ch in parts[1] if ch.isdigit()))
            if start <= code2 <= end:
                return True
        except Exception:
            pass
    else:
        digits = ''.join(ch for ch in desired_s if ch.isdigit())
        if digits and code2 is not None:
            try:
                want = int(digits[:2].rjust(2, '0'))
                if want == code2:
                    return True
            except Exception:
                pass

    # 3) Backward-compatible free-text match (e.g., "IT")
    industry_text = _effective_industry_text(data)
    if desired_s.lower() in str(industry_text).lower():
        return True

    return False


def _dedupe_list_of_dicts(items, keys):
    seen, out = set(), []
    for it in items or []:
        if not isinstance(it, dict):
            continue
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


def _get_dart_api_key():
    # Prefer per-process override via env var, then fallback to Django settings
    return os.environ.get('DART_API_KEY') or getattr(settings, 'DART_API_KEY', None)


def _fetch_company_overview_via_dart_api(corp_code):
    """Fetch company overview via OpenDART REST API company.json.

    Requires 8-digit corp_code.
    Docs: https://opendart.fss.or.kr/
    """

    api_key = _get_dart_api_key()
    if not api_key:
        return None

    if not corp_code or not (isinstance(corp_code, str) and corp_code.isdigit() and len(corp_code) == 8):
        return None

    url = 'https://opendart.fss.or.kr/api/company.json'
    try:
        resp = requests.get(url, params={'crtfc_key': api_key, 'corp_code': corp_code}, timeout=30)
        resp.raise_for_status()
        data = resp.json() if resp.content else None
    except Exception:
        return None

    if not isinstance(data, dict):
        return None

    # DART returns status/message on failure
    if data.get('status') and str(data.get('status')) != '000':
        return None

    adres = data.get('adres') or data.get('addr') or data.get('address')
    industry = data.get('induty') or data.get('industry')
    induty_code = data.get('induty_code') or data.get('industry_code')

    return {
        'ceo_nm': data.get('ceo_nm') or data.get('ceoNm'),
        'addr': adres,
        'adres': adres,
        'industry': industry,
        'industry_code': induty_code,
        'induty_code': induty_code,
        'est_dt': data.get('est_dt') or data.get('estDt'),
        'region': extract_region_from_address(adres),
        'raw': data,
    }


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
    api_key = _get_dart_api_key()
    if not api_key:
        return None

    # Prefer OpenDartReader when available, but fall back to REST API on failure.
    raw = None
    if OpenDartReader:
        try:
            odr = OpenDartReader(api_key)
            raw = odr.company(corp)
        except Exception:
            raw = None

    # If OpenDartReader failed or returned empty, try official REST API (requires corp_code)
    if not raw:
        corp_code = None
        if isinstance(corp, str) and corp.isdigit() and len(corp) == 8:
            corp_code = corp
        return _fetch_company_overview_via_dart_api(corp_code)

    if not isinstance(raw, dict):
        return None

    adres = raw.get('adres') or raw.get('addr') or raw.get('address')
    industry = raw.get('induty') or raw.get('industry')
    induty_code = raw.get('induty_code') or raw.get('industry_code')

    return {
        'ceo_nm': raw.get('ceo_nm') or raw.get('ceoNm'),
        'addr': adres,
        'adres': adres,
        'industry': industry,
        'industry_code': induty_code,
        'induty_code': induty_code,
        'est_dt': raw.get('est_dt') or raw.get('estDt'),
        'region': extract_region_from_address(adres),
        'raw': raw,
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
    desired_sizes = _as_str_list(prefs.get('desired_size'))
    company_size = _effective_company_size(data)
    if desired_sizes and company_size and company_size in desired_sizes:
        score += 1.0
    # safe check: prefs.location may be None; avoid `None in <string>` TypeError
    pref_loc = prefs.get('location')
    region_str = (_effective_region(data) or '')
    if pref_loc and isinstance(region_str, str) and pref_loc in region_str:
        score += 0.5
    desired_industries = _as_str_list(prefs.get('desired_industries'))
    if desired_industries:
        if any(_matches_industry_pref(ind, data) for ind in desired_industries):
            score += 1.0

    return score


from django.core.exceptions import ObjectDoesNotExist

def recommend_companies(prefs, top_n=10):
    results = []

    desired_sizes = _as_str_list(prefs.get('desired_size'))
    desired_industries = _as_str_list(prefs.get('desired_industries'))
    desired_region = prefs.get('location')

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

        # Strict filters: when the user selected criteria, only keep matching companies.
        company_size = _effective_company_size(data)
        if desired_sizes and (not company_size or company_size not in desired_sizes):
            continue

        if desired_region:
            region_str = _effective_region(data)
            if not region_str or desired_region not in str(region_str):
                continue

        if desired_industries:
            if not any(_matches_industry_pref(ind, data) for ind in desired_industries):
                continue

        score = score_company_for_user(prefs, data)

        results.append({
            'company_id': c.id,
            'corp_name': c.corp_name,
            'company_size': company_size,
            'score': score,
            'profile': data,
        })

    # NOTE: Many users end up with a small discrete score space (0.0/0.5/1.0/1.5/2.5).
    # When many companies tie, Python's stable sort plus stable DB iteration order can
    # produce the same top-N list every time. We keep score ordering, but randomize
    # within ties to improve result variety.
    for it in results:
        it['_tie'] = random.random()
    results.sort(key=lambda x: (x['score'], x['_tie']), reverse=True)
    for it in results:
        it.pop('_tie', None)
    return results[:top_n]


def build_fixed_companyprofile_payload():
    raise NotImplementedError('Use build_fixed_companyprofile_payload(company, existing_data)')


def _extract_industry_fields_from_raw(raw):
    """Best-effort extraction of industry fields from a stored raw overview dict."""
    if not isinstance(raw, dict):
        return {}

    industry_code = raw.get('industry_code') or raw.get('induty_code') or raw.get('indutyCode')
    industry_name = raw.get('industry_name') or raw.get('induty') or raw.get('industry')

    # Normalize code to digits-only string when possible
    if industry_code is not None:
        try:
            s = str(industry_code).strip()
            digits = ''.join(ch for ch in s if ch.isdigit())
            industry_code = digits or s
        except Exception:
            pass

    return {
        'industry_code': industry_code,
        'industry_name': industry_name,
    }


def build_fixed_companyprofile_payload(company, existing_data=None):
    """Return a stable CompanyProfile.data schema for a given company.

    This is used by backfill commands to ensure required keys exist.
    It should be safe to MERGE into existing data.
    """

    existing_data = existing_data if isinstance(existing_data, dict) else {}
    c = company

    # Core identifiers
    try:
        stock_code = (getattr(c, 'stock_code', None) or '').strip() or None
    except Exception:
        stock_code = None

    # Pull known fields from existing data
    financials = existing_data.get('financials')
    latest_disclosures = existing_data.get('latest_disclosures')
    company_size = existing_data.get('company_size')

    overview = existing_data.get('company_overview')
    overview = overview if isinstance(overview, dict) else {}

    # Ensure raw is preserved if present
    raw = overview.get('raw') if isinstance(overview.get('raw'), dict) else None
    if raw:
        norm = _extract_industry_fields_from_raw(raw)
        if norm.get('industry_code') and not (overview.get('industry_code') or overview.get('induty_code')):
            overview['industry_code'] = norm.get('industry_code')
            overview['induty_code'] = norm.get('industry_code')

    # Ensure region best-effort
    if not overview.get('region'):
        addr = overview.get('addr') or overview.get('adres')
        if addr:
            overview['region'] = extract_region_from_address(addr)

    # Ensure company_size best-effort
    if company_size is None:
        try:
            company_size = classify_company_size(stock_code, financials)
        except Exception:
            company_size = None

    # Keep overview schema stable across companies
    required_overview_keys = [
        'ceo_nm',
        'addr',
        'adres',
        'industry',
        'industry_code',
        'induty_code',
        'est_dt',
        'region',
        'company_size',
        'raw',
    ]
    for k in required_overview_keys:
        if k not in overview:
            overview[k] = None

    # Never keep duplicated identifiers inside overview
    for k in ['corp_name', 'corp_code', 'stock_code']:
        overview.pop(k, None)

    # Mirror company_size into overview for easier UI consumption
    overview['company_size'] = company_size

    return {
        'corp_name': getattr(c, 'corp_name', None),
        'corp_code': getattr(c, 'corp_code', None),
        'stock_code': stock_code,
        'financials': financials,
        'latest_disclosures': latest_disclosures,
        'company_size': company_size,
        # Keep key present for schema stability; may be filled by other pipeline
        'industry_outlook': existing_data.get('industry_outlook'),
        # Optional counters used elsewhere
        'num_disclosures_365d': existing_data.get('num_disclosures_365d'),
        'company_overview': overview,
    }