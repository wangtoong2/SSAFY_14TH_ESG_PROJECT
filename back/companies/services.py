import datetime
import json
import os
from django.utils import timezone
from django.conf import settings
from .models import Company, CompanyProfile
from .api import get_corporate_disclosure_data

try:
    from OpenDartReader import OpenDartReader
except Exception:
    OpenDartReader = None


# ESG-specific keyword detection removed per user request


def fetch_company_data(corp_name, days=365):
    """
    주어진 기업명(corp_name)을 바탕으로 DART 공시 데이터를 호출하고
    추천에 사용할 요약 정보를 반환합니다.

        반환 예시 구조:
        {
            'corp_name': '삼성전자',
            'corp_code': '00126380',
            'num_disclosures_365d': 12,
            'latest_disclosures': [ { 'date':'20250101', 'title':'...'}, ... ],
            'financials': { ... },
            'company_overview': { ... }
        }
    """
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    start_str = start.strftime('%Y%m%d')
    end_str = end.strftime('%Y%m%d')

    resp = get_corporate_disclosure_data(corp_name, start_str, end_str)

    result = {
        'corp_name': corp_name,
        'corp_code': None,
        'num_disclosures_365d': 0,
        'latest_disclosures': [],
        'financials': None,
        'company_overview': None,
        'company_size': None,
        'industry_outlook': None,
    }

    if not resp or 'error' in resp:
        return result

    # DART search.json returns 'list' with disclosure items
    items = resp.get('list') or []

    result['num_disclosures_365d'] = len(items)

    latest = []
    for it in items[:5]:
        latest.append({
            'date': it.get('rcept_dt') or it.get('disclosure_date') or it.get('report_tp'),
            'title': it.get('report_nm') or it.get('title') or it.get('summary') or it.get('title'),
            'type': it.get('rpt_nm') or it.get('document_type')
        })

    result['latest_disclosures'] = latest

    # try to get corp_code from response list items
    if items and items[0].get('corp_code'):
        result['corp_code'] = items[0].get('corp_code')

    # detect ESG related disclosures
    titles = [d.get('title') or d.get('report_nm') or '' for d in items]
    # ESG keyword detection removed; titles still stored in `latest_disclosures`

    # attach simple financial summary if OpenDartReader is available
    try:
        fin = fetch_financial_summary(corp_name)
        result['financials'] = fin
        if fin and fin.get('corp_code') and not result['corp_code']:
            result['corp_code'] = fin.get('corp_code')
    except Exception:
        result['financials'] = None

    # fetch company overview (industry, CEO, addr etc.)
    try:
        overview = fetch_company_overview(corp_name)
        result['company_overview'] = overview
    except Exception:
        result['company_overview'] = None

    # classify company size
    try:
        result['company_size'] = classify_company_size(result.get('stock_code'), result.get('financials'))
    except Exception:
        result['company_size'] = None

    # compute industry outlook
    try:
        result['industry_outlook'] = compute_industry_outlook(result.get('financials'), result.get('num_disclosures_365d'))
    except Exception:
        result['industry_outlook'] = None

    return result


def _parse_amount(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return v
    s = str(v)
    s = s.replace(',', '').replace('\u200b', '').strip()
    if s == '' or s == '-' or s == '':
        return None
    try:
        return int(float(s))
    except Exception:
        return None


def fetch_financial_summary(corp, latest_years=2):
    """OpenDartReader로부터 최근 사업연도 재무제표를 가져와 요약합니다.

    반환 예시:
    {
      'corp_code': '00126380',
      'years': { '2024': { 'revenue': 100000, 'operating_income': 5000, 'net_income': 3000 }, ... },
      'latest_year': 2024,
      'revenue_growth': 0.12
    }
    """
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
            df = None

        if df is None or df.empty:
            continue

        # Try to set corp_code
        if out['corp_code'] is None and hasattr(df, 'corp_code'):
            try:
                out['corp_code'] = df.get('corp_code').iloc[0]
            except Exception:
                pass

        # look for common account names
        def find_amount(df, keywords):
            for kw in keywords:
                row = df[df['account_nm'].str.contains(kw, na=False)]
                if not row.empty:
                    val = row.iloc[0].get('thstrm_amount') or row.iloc[0].get('thstrm_amount')
                    return _parse_amount(val)
            return None

        revenue = find_amount(df, ['매출', '수익', '영업수익', '매출액'])
        operating = find_amount(df, ['영업이익'])
        net = find_amount(df, ['당기순이익', '순이익', '계속영업이익(손실)'])

        out['years'][str(y)] = {'revenue': revenue, 'operating_income': operating, 'net_income': net}

        if prev_revenue is not None and revenue is not None:
            out['revenue_growth'] = None if prev_revenue in (0, None) else (revenue - prev_revenue) / prev_revenue

        prev_revenue = revenue

    if out['years']:
        out['latest_year'] = max(int(k) for k in out['years'].keys())

    return out


def fetch_company_overview(corp):
    """Fetch company overview (industry, CEO, addr, etc.) via OpenDartReader/company API.

    Returns a summary dict with common keys and raw response under 'raw'.
    """
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

    summary = {}
    for k in ['corp_code', 'corp_name', 'stock_code', 'ceo_nm', 'addr', 'est_dt', 'induty']:
        if k in raw:
            summary[k] = raw.get(k)

    # try to extract any industry-like field
    for k, v in (raw.items() if isinstance(raw, dict) else []):
        lk = k.lower()
        if 'ind' in lk or 'industry' in lk or 'biz' in lk:
            summary.setdefault('industry', v)
            break

    # fallback candidates
    for cand in ['induty_code', 'induty_nm', 'induty_cd', 'biz_tp', 'biz_type', 'industry_nm']:
        if cand in raw and 'industry' not in summary:
            summary['industry'] = raw.get(cand)
            break

    summary['raw'] = raw
    return summary


def classify_company_size(stock_code, financials):
    """Classify company size as '중소', '중견', or '대기업'.

    Uses stock_code presence as a hint (listed -> larger) and revenue thresholds when available.
    """
    # if no financials provided, guess based on listing
    if not financials:
        return '대기업' if stock_code else '중소'

    years = financials.get('years') or {}
    if not years:
        return '대기업' if stock_code else '중소'

    latest = financials.get('latest_year')
    rev = None
    if latest and str(latest) in years:
        rev = years[str(latest)].get('revenue')
    else:
        for yv in years.values():
            if yv.get('revenue'):
                rev = yv.get('revenue')
                break

    if rev is None:
        return '대기업' if stock_code else '중소'

    # thresholds in KRW
    SMALL_MAX = 100_000_000_000  # 1,000억
    LARGE_MIN = 1_000_000_000_000  # 1조

    try:
        if rev >= LARGE_MIN:
            return '대기업'
        if rev >= SMALL_MAX:
            return '중견'
        return '중소'
    except Exception:
        return '중소'


def compute_industry_outlook(financials, num_disclosures):
    """단순 휴리스틱으로 산업 전망 점수/라벨 산출 (ESG 요소 제외).

    score = 0.7 * revenue_growth + 0.3 * disclosure_factor
    - revenue_growth: -1..+inf (clamped to [-1,1])
    - disclosure_factor: min(num_disclosures/10, 1)
    라벨: score > 0.1 -> '긍정적', score < -0.05 -> '부정적', else '중립'
    """
    rev_growth = 0.0
    if financials and financials.get('revenue_growth') is not None:
        try:
            rev_growth = float(financials.get('revenue_growth'))
        except Exception:
            rev_growth = 0.0

    rev_growth = max(min(rev_growth, 1.0), -1.0)
    disclosure_factor = min(num_disclosures / 10.0, 1.0) if num_disclosures is not None else 0.0

    score = 0.7 * rev_growth + 0.3 * disclosure_factor

    if score > 0.1:
        label = '긍정적'
    elif score < -0.05:
        label = '부정적'
    else:
        label = '중립'

    return {'score': score, 'label': label}


def fetch_all_companies_to_file(output_path='companies_dart_cache.json'):
    """데이터베이스의 `Company` 전체를 순회하며 DART 요약을 호출하고 파일로 저장합니다."""
    qs = Company.objects.all()
    out = []
    for c in qs:
        try:
            data = fetch_company_data(c.corp_name)
            data['stock_code'] = c.stock_code
            out.append(data)
            # save to DB cache (upsert CompanyProfile)
            try:
                if c.profile_id or hasattr(c, 'profile'):
                    # update existing
                    CompanyProfile.objects.update_or_create(company=c, defaults={'data': data})
                else:
                    CompanyProfile.objects.update_or_create(company=c, defaults={'data': data})
            except Exception:
                # ignore DB cache failures but continue
                pass
        except Exception as e:
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


def recommend_companies(prefs, top_n=10, use_db_cache=True):
    """Return top-N companies matching `prefs`.

    prefs: see `score_company_for_user` for keys.
    use_db_cache: if True, read `CompanyProfile.data` for ranking; otherwise calls `fetch_company_data` live.

    Returns list of dicts: { 'company_id', 'corp_name', 'score', 'breakdown', 'profile' }
    """
    results = []
    qs = Company.objects.all()
    for c in qs:
        profile = None
        if use_db_cache:
            try:
                profile = getattr(c, 'profile').data if hasattr(c, 'profile') and c.profile is not None else None
            except Exception:
                profile = None

        if not profile:
            try:
                profile = fetch_company_data(c.corp_name)
            except Exception:
                profile = None

        if not profile:
            continue

        score, breakdown = score_company_for_user(prefs, profile)
        results.append({
            'company_id': c.id,
            'corp_name': c.corp_name,
            'score': score,
            'breakdown': breakdown,
            'profile': profile,
        })

    # sort by score desc
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_n]
