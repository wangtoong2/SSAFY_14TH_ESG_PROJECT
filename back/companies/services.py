import datetime
import json
import logging
import os
import time
import requests
from django.conf import settings
from .models import Company, CompanyProfile
from .api import get_corporate_disclosure_data

try:
    from OpenDartReader import OpenDartReader
except Exception:
    OpenDartReader = None

logger = logging.getLogger(__name__)


def _canonical_stock_code(v):
    if v is None:
        return None
    try:
        s = str(v).strip()
    except Exception:
        return None
    return s or None


def extract_region_from_address(addr):
    """Extract a top-level region (시/도) from a Korean address string.

    Examples:
      - '서울특별시 강남구 ...' -> '서울특별시'
      - '경기도 성남시 ...' -> '경기도'
      - '세종특별자치시 ...' -> '세종특별자치시'
    """
    if not addr:
        return None
    try:
        first = str(addr).strip().split()[0]
    except Exception:
        return None
    if not first:
        return None

    # Normalize common city/province names
    mapping_prefix = {
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
    for k, v in mapping_prefix.items():
        if first.startswith(k):
            return v

    # If it already looks like a full region, return as-is
    if any(suffix in first for suffix in ['특별자치시', '특별자치도', '광역시', '특별시']) or first.endswith('도'):
        return first

    return first


def _extract_industry_fields_from_raw(raw):
    """Normalize industry code/name from raw DART company response dict."""
    if not isinstance(raw, dict):
        return {}
    industry_code = None
    industry_name = None
    code_candidates = ['induty_code', 'induty_cd', 'industry_cd', 'industry_code', 'indutyCode', 'industryCd']
    name_candidates = ['induty_nm', 'induty_name', 'industry_nm', 'industry_name', 'biz_tp', 'biz_type']
    for k in code_candidates:
        if k in raw and raw.get(k):
            industry_code = raw.get(k)
            break
    for k in name_candidates:
        if k in raw and raw.get(k):
            industry_name = raw.get(k)
            break
    out = {}
    if industry_code:
        out['industry_code'] = industry_code
    if industry_name:
        out['industry_name'] = industry_name
    return out


def _dedupe_list_of_dicts(items, key_fields):
    """Remove duplicate dict entries from a list preserving order.

    key_fields: list of keys to form a uniqueness tuple; missing keys use None.
    """
    seen = set()
    out = []
    for it in items or []:
        if not isinstance(it, dict):
            # fall back to string representation
            k = tuple([str(it)])
        else:
            k = tuple(it.get(f) for f in key_fields)
        if k in seen:
            continue
        seen.add(k)
        out.append(it)
    return out


# ESG-specific keyword detection removed per user request


def fetch_company_data(corp_name, days=365):
    """
    DART 기반 기업 원본 데이터 수집
    (company_size는 여기서 계산하지 않는다!)
    """
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)

    resp = get_corporate_disclosure_data(
        corp_name,
        start.strftime('%Y%m%d'),
        end.strftime('%Y%m%d')
    )

    is_corp_code = isinstance(corp_name, str) and corp_name.isdigit() and len(corp_name) == 8

    result = {
        # corp_code로 호출될 수 있으므로, 실제 기업명은 overview에서 채우는 것을 우선한다.
        'corp_name': None if is_corp_code else corp_name,
        'corp_code': None,
        'num_disclosures_365d': 0,
        'latest_disclosures': [],
        'financials': None,
        'company_overview': None,
        'company_size': None,      # ❗ placeholder
        'industry_outlook': None,
    }

    if not resp or 'error' in resp:
        return result

    items = resp.get('list') or []
    # dedupe items by reception date, report name and reception number if present
    items = _dedupe_list_of_dicts(items, ['rcept_dt', 'report_nm', 'rcept_no'])
    result['num_disclosures_365d'] = len(items)

    latest = []
    for it in items[:5]:
        latest.append({
            'date': it.get('rcept_dt'),
            'title': it.get('report_nm'),
            'type': it.get('rpt_nm')
        })
    # remove duplicate disclosure dicts by date+title
    result['latest_disclosures'] = _dedupe_list_of_dicts(latest, ['date', 'title'])

    if items and items[0].get('corp_code'):
        result['corp_code'] = items[0]['corp_code']

    # 재무 데이터
    result['financials'] = fetch_financial_summary(corp_name)

    # 기업 개요
    overview = fetch_company_overview(corp_name)
    result['company_overview'] = overview

    # overview가 실제 기업명/기업코드를 주면 top-level에도 반영
    try:
        if isinstance(overview, dict):
            ov_name = overview.get('corp_name')
            ov_code = overview.get('corp_code')
            if ov_name:
                result['corp_name'] = ov_name
            if ov_code:
                result['corp_code'] = ov_code
    except Exception:
        pass

    # company_overview는 보조 정보만 보관: top-level과 중복되는 키 제거
    try:
        if isinstance(result.get('company_overview'), dict):
            sanitized = dict(result['company_overview'])
            for k in ['corp_name', 'corp_code', 'stock_code']:
                sanitized.pop(k, None)
            result['company_overview'] = sanitized
    except Exception:
        pass

    # corp_code로 호출된 경우 top-level corp_code는 입력값을 기본으로 채움
    if result.get('corp_code') is None and is_corp_code:
        result['corp_code'] = corp_name

    # 산업 전망
    result['industry_outlook'] = compute_industry_outlook(
        result['financials'],
        result['num_disclosures_365d']
    )

    return result

def _parse_amount(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return v
    s = str(v).replace(',', '').strip()
    if s in ('', '-', 'None'):
        return None
    try:
        return int(float(s))
    except Exception:
        return None


def fetch_financial_summary(corp, latest_years=2):
    # Prefer per-process override via env var, then fallback to Django settings
    api_key = os.environ.get('DART_API_KEY') or getattr(settings, 'DART_API_KEY', None)
    if not OpenDartReader or not api_key:
        return None

    odr = OpenDartReader(api_key)
    current_year = datetime.date.today().year
    years = [current_year - i for i in range(1, latest_years + 1)]

    out = {'corp_code': None, 'years': {}, 'latest_year': None, 'revenue_growth': None}
    prev_revenue = None

    for y in years:
        try:
            df = odr.finstate_all(corp, bsns_year=y, reprt_code='11011', fs_div='CFS')
        except Exception:
            continue

        if df is None or df.empty:
            continue

        def find_amount(keywords):
            if 'account_nm' not in df.columns:
                return None
            for kw in keywords:
                try:
                    row = df[df['account_nm'].str.contains(kw, na=False)]
                except Exception:
                    continue
                if not row.empty:
                    return _parse_amount(row.iloc[0].get('thstrm_amount'))
            return None

        revenue = find_amount(['매출', '매출액'])
        operating = find_amount(['영업이익'])
        net = find_amount(['당기순이익'])
        # capital / equity (자본금, 자본총계 등)
        capital = find_amount(['자본금', '자본총계', '자본'])

        out['years'][str(y)] = {
            'revenue': revenue,
            'operating_income': operating,
            'net_income': net,
            'capital': capital
        }

        if prev_revenue not in (None, 0) and revenue is not None:
            try:
                out['revenue_growth'] = (revenue - prev_revenue) / prev_revenue
            except Exception:
                out['revenue_growth'] = None

        prev_revenue = revenue

    if out['years']:
        out['latest_year'] = max(map(int, out['years'].keys()))
        # set latest capital if available
        try:
            latest = out['latest_year']
            lc = out['years'].get(str(latest), {}).get('capital')
            out['latest_capital'] = lc
        except Exception:
            out['latest_capital'] = None

    return out


def fetch_company_overview(corp):
    # Prefer per-process override via env var, then fallback to Django settings
    api_key = os.environ.get('DART_API_KEY') or getattr(settings, 'DART_API_KEY', None)
    raw = None
    # Prefer OpenDartReader if available (parses nicely)
    if OpenDartReader and api_key:
        try:
            odr = OpenDartReader(api_key)
            raw = odr.company(corp)
        except Exception:
            try:
                raw_list = odr.company_by_name(corp)
                raw = raw_list[0] if raw_list else None
            except Exception:
                raw = None
    else:
        # HTTP fallback to DART public API (corp_code or corp_name)
        try:
            url = 'https://opendart.fss.or.kr/api/company.json'
            params = {'crtfc_key': api_key}
            # if input looks like corp_code (all digits and length 8), use corp_code param
            if isinstance(corp, str) and corp.isdigit() and len(corp) >= 6:
                params['corp_code'] = corp
            else:
                params['corp_name'] = corp
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            jr = r.json()
            # DART returns {'status': '000', ...} for success
            raw = jr
        except Exception:
            raw = None

    if not raw:
        return None

    summary = {
        'corp_code': raw.get('corp_code'),
        'corp_name': raw.get('corp_name'),
        'stock_code': raw.get('stock_code'),
        'ceo_nm': raw.get('ceo_nm'),
        # DART company.json uses 'adres'
        'addr': raw.get('addr') or raw.get('adres'),
        # 원본 키도 함께 보관(요청 스키마 호환)
        'adres': raw.get('adres') or raw.get('addr') or (raw.get('addr') or raw.get('adres')),
        'est_dt': raw.get('est_dt'),
        # 기존 호환용 (문자열)
        'industry': raw.get('induty') or raw.get('industry_nm') or raw.get('biz_type'),
        # only store raw when it's a valid company payload, not an API error
        'raw': raw if not (isinstance(raw, dict) and (str(raw.get('status','')).startswith('0') and '사용한도' in str(raw.get('message','')))) else None,
    }

    # ✅ 여기서 정규화 함수 연결
    try:
        norm = _extract_industry_fields_from_raw(raw)
        summary.update(norm)
        # → industry_code, industry_name 들어감
    except Exception:
        pass

    # 요청 스키마 키: induty_code
    try:
        summary['induty_code'] = summary.get('induty_code') or summary.get('industry_code') or raw.get('induty_code')
    except Exception:
        pass

    # 지역 추출 (주소의 시/도 레벨)
    try:
        addr = summary.get('addr')
        summary['region'] = extract_region_from_address(addr) if addr else None
    except Exception:
        summary['region'] = None

    return summary


def classify_company_size(stock_code, financials):
    """
    company_size는 파생 데이터
    → 정보 부족 시 '중소' ❌ / None ⭕
    """

    if not stock_code and not financials:
        return None

    if stock_code and not financials:
        return '중견'

    years = financials.get('years', {})
    if not years:
        return '중견' if stock_code else None

    latest = financials.get('latest_year')
    rev = None
    if latest and str(latest) in years:
        rev = years[str(latest)].get('revenue')

    if rev is None:
        return '중견' if stock_code else None

    if rev >= 1_000_000_000_000:
        return '대기업'
    elif rev >= 100_000_000_000:
        return '중견'
    else:
        return '중소'


def build_fixed_companyprofile_payload(company, data):
    """Build a stable response schema regardless of how `data` is stored.

    Output shape (keys always present):
      {
        corp_name, corp_code,
        company_overview: {ceo_nm, addr, industry, adres, induty_code, est_dt, region, company_size},
        industry_outlook
      }
    """

    data = data if isinstance(data, dict) else {}
    overview = data.get('company_overview')
    overview = overview if isinstance(overview, dict) else {}
    raw = overview.get('raw') if isinstance(overview.get('raw'), dict) else None

    # Prefer normalized fields; fall back to raw DART keys where possible.
    addr = overview.get('addr') or (raw.get('adres') if raw else None) or (raw.get('addr') if raw else None)
    ceo_nm = overview.get('ceo_nm') or (raw.get('ceo_nm') if raw else None)
    industry = overview.get('industry')

    adres = overview.get('adres') or (raw.get('adres') if raw else None) or addr
    induty_code = (
        overview.get('induty_code')
        or overview.get('industry_code')
        or (raw.get('induty_code') if raw else None)
        or (raw.get('industry_code') if raw else None)
        or (raw.get('induty_cd') if raw else None)
    )
    est_dt = overview.get('est_dt') or (raw.get('est_dt') if raw else None)

    region = overview.get('region') or extract_region_from_address(addr)

    # company_size: prefer precomputed, else compute from canonical inputs.
    company_size = overview.get('company_size') or data.get('company_size')
    if company_size is None:
        try:
            stock_code = _canonical_stock_code(data.get('stock_code') or getattr(company, 'stock_code', None))
            company_size = classify_company_size(stock_code, data.get('financials'))
        except Exception:
            company_size = None

    industry_outlook = data.get('industry_outlook')

    payload = {
        'corp_name': getattr(company, 'corp_name', None) or data.get('corp_name'),
        'corp_code': getattr(company, 'corp_code', None) or data.get('corp_code'),
        'company_overview': {
            'ceo_nm': ceo_nm,
            'addr': addr,
            'industry': industry,
            'adres': adres,
            'induty_code': induty_code,
            'est_dt': est_dt,
            'region': region,
            'company_size': company_size,
        },
        'industry_outlook': industry_outlook,
    }
    return payload


def compute_industry_outlook(financials, num_disclosures):
    rev_growth = financials.get('revenue_growth', 0.0) if financials else 0.0
    rev_growth = max(min(rev_growth or 0.0, 1.0), -1.0)

    disclosure_factor = min((num_disclosures or 0) / 10.0, 1.0)
    score = 0.7 * rev_growth + 0.3 * disclosure_factor

    if score > 0.1:
        label = '긍정적'
    elif score < -0.05:
        label = '부정적'
    else:
        label = '중립'

    return {'score': score, 'label': label}


def fetch_all_companies_to_file(output_path='companies_dart_cache.json'):
    qs = Company.objects.select_related('profile').all()
    total = qs.count()
    out = []
    err_path = os.path.join(os.getcwd(), 'fetch_dart_errors.log')
    with open(err_path, 'a', encoding='utf-8') as err_log:
        for idx, c in enumerate(qs, 1):
            try:
                print(f"[{idx}/{total}] {c.corp_name}")
                data = fetch_company_data(c.corp_name)

                # ensure stock_code and recompute company_size
                data['stock_code'] = c.stock_code
                try:
                    data['company_size'] = classify_company_size(c.stock_code, data.get('financials'))
                except Exception:
                    data['company_size'] = data.get('company_size')

                try:
                    CompanyProfile.objects.update_or_create(company=c, defaults={'data': data})
                except Exception as db_e:
                    err_log.write(f"DB error {c.corp_name}: {db_e}\n")
                    err_log.flush()
                    logger.exception("DB save error for %s", c.corp_name)

                out.append(data)
                time.sleep(0.05)
            except Exception as e:
                err_log.write(f"Fetch error {c.corp_name}: {e}\n")
                err_log.flush()
                logger.exception("Fetch error for %s", c.corp_name)
                out.append({'corp_name': c.corp_name, 'error': str(e)})

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    return output_path


def _match_weight(match, weight=1.0):
    return weight if match else 0.0


def score_company_for_user(prefs, company_data):
    """Score a single company against `prefs`.

    prefs (dict) possible keys:
      - `desired_industries`: list of industry names (strings)
      - `desired_size`: one of ['중소','중견','대기업'] or list
      - `min_revenue`: int (원 단위)
      - `location`: string (matches `company_overview.addr`)
      - `keywords`: list of strings to match in latest_disclosures titles
      - `min_growth`: float (e.g., 0.05 for 5%)
      - `weights`: dict of weights for components

    Returns: float score (higher = better) and breakdown dict
    """
    weights = {'industry': 2.0, 'size': 1.0, 'revenue': 1.0, 'growth': 1.0, 'location': 0.5, 'keywords': 1.0}
    if prefs.get('weights'):
        weights.update(prefs.get('weights'))

    score = 0.0
    breakdown = {}

    # industry match
    desired_inds = prefs.get('desired_industries') or []
    comp_ind = None
    if company_data.get('company_overview'):
        comp_ind = company_data['company_overview'].get('industry')
    industry_match = False
    if desired_inds and comp_ind:
        for di in desired_inds:
            if di.lower() in str(comp_ind).lower():
                industry_match = True
                break
    elif not desired_inds:
        industry_match = True

    industry_score = _match_weight(industry_match, weights['industry'])
    score += industry_score
    breakdown['industry'] = industry_score

    # size match
    desired_size = prefs.get('desired_size')
    size_match = False
    comp_size = company_data.get('company_size')
    if desired_size:
        if isinstance(desired_size, (list, tuple)):
            size_match = comp_size in desired_size
        else:
            size_match = comp_size == desired_size
    else:
        size_match = True
    size_score = _match_weight(size_match, weights['size'])
    score += size_score
    breakdown['size'] = size_score

    # revenue
    min_rev = prefs.get('min_revenue')
    rev_score = 0.0
    fin = company_data.get('financials') or {}
    if min_rev and fin:
        latest = fin.get('latest_year')
        rev = None
        if latest and str(latest) in fin.get('years', {}):
            rev = fin['years'][str(latest)].get('revenue')
        else:
            for yv in fin.get('years', {}).values():
                if yv.get('revenue'):
                    rev = yv.get('revenue')
                    break
        if rev is not None:
            try:
                rev_score = weights['revenue'] * (1.0 if rev >= min_rev else float(rev) / (min_rev * 1.0))
            except Exception:
                rev_score = 0.0
    else:
        rev_score = weights['revenue'] * 0.5
    score += rev_score
    breakdown['revenue'] = rev_score

    # growth
    min_growth = prefs.get('min_growth')
    growth_score = 0.0
    if min_growth and fin and fin.get('revenue_growth') is not None:
        rg = fin.get('revenue_growth')
        try:
            rg = float(rg)
        except Exception:
            rg = 0.0
        growth_score = weights['growth'] * (1.0 if rg >= min_growth else max(0.0, rg / (min_growth or 1)))
    else:
        growth_score = 0.0
    score += growth_score
    breakdown['growth'] = growth_score

    # location
    loc_pref = prefs.get('location')
    loc_score = 0.0
    addr = None
    if company_data.get('company_overview'):
        addr = company_data['company_overview'].get('addr')
    if loc_pref and addr:
        loc_score = _match_weight(loc_pref.lower() in addr.lower(), weights['location'])
    elif not loc_pref:
        loc_score = weights['location'] * 0.5
    score += loc_score
    breakdown['location'] = loc_score

    # keywords in disclosures
    keys = prefs.get('keywords') or []
    kw_score = 0.0
    if keys:
        titles = [d.get('title','') for d in (company_data.get('latest_disclosures') or [])]
        matches = 0
        for k in keys:
            for t in titles:
                if k.lower() in t.lower():
                    matches += 1
                    break
        if matches:
            kw_score = weights['keywords'] * (matches / len(keys))
    else:
        kw_score = weights['keywords'] * 0.5
    score += kw_score
    breakdown['keywords'] = kw_score

    # ESG preference removed per user request

    return score, breakdown


def recommend_companies(prefs, top_n=10):
    results = []

    qs = Company.objects.select_related('profile').all()
    for c in qs.iterator():
        profile = getattr(c, 'profile', None)
        if not profile:
            continue

        data = profile.data or {}

        # ensure company_size available
        if data.get('company_size') is None:
            try:
                data['company_size'] = classify_company_size(c.stock_code, data.get('financials'))
            except Exception:
                data['company_size'] = None

        score, breakdown = score_company_for_user(prefs, data)
        results.append({
            'company_id': c.id,
            'corp_name': c.corp_name,
            'company_size': data.get('company_size'),
            'score': score,
            'breakdown': breakdown,
            'profile': data,
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_n]
