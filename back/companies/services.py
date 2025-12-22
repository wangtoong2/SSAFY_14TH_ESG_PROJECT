import datetime
import json
import logging
import os
import time
from django.conf import settings
from .models import Company, CompanyProfile
from .api import get_corporate_disclosure_data

try:
    from OpenDartReader import OpenDartReader
except Exception:
    OpenDartReader = None

logger = logging.getLogger(__name__)


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

    result = {
        'corp_name': corp_name,
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
    result['num_disclosures_365d'] = len(items)

    result['latest_disclosures'] = [
        {
            'date': it.get('rcept_dt'),
            'title': it.get('report_nm'),
            'type': it.get('rpt_nm')
        }
        for it in items[:5]
    ]

    if items and items[0].get('corp_code'):
        result['corp_code'] = items[0]['corp_code']

    # 재무 데이터
    result['financials'] = fetch_financial_summary(corp_name)

    # 기업 개요
    result['company_overview'] = fetch_company_overview(corp_name)

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
    api_key = getattr(settings, 'DART_API_KEY', None) or os.environ.get('DART_API_KEY')
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

        out['years'][str(y)] = {
            'revenue': revenue,
            'operating_income': operating,
            'net_income': net
        }

        if prev_revenue not in (None, 0) and revenue is not None:
            try:
                out['revenue_growth'] = (revenue - prev_revenue) / prev_revenue
            except Exception:
                out['revenue_growth'] = None

        prev_revenue = revenue

    if out['years']:
        out['latest_year'] = max(map(int, out['years'].keys()))

    return out


def fetch_company_overview(corp):
    api_key = getattr(settings, 'DART_API_KEY', None) or os.environ.get('DART_API_KEY')
    if not OpenDartReader or not api_key:
        return None

    odr = OpenDartReader(api_key)
    raw = None
    try:
        raw = odr.company(corp)
    except Exception:
        try:
            raw_list = odr.company_by_name(corp)
            raw = raw_list[0] if raw_list else None
        except Exception:
            raw = None

    if not raw:
        return None

    summary = {
        'corp_code': raw.get('corp_code'),
        'corp_name': raw.get('corp_name'),
        'stock_code': raw.get('stock_code'),
        'ceo_nm': raw.get('ceo_nm'),
        'addr': raw.get('addr'),
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
